import { useState, useEffect } from 'react';

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function searchNotes({ q = '', tagId = null, page = 1, pageSize = 10, sort = 'created_desc' } = {}) {
  const params = new URLSearchParams();
  if (q && q.trim()) {
    params.set('q', q.trim());
  }
  if (tagId) {
    params.set('tag_id', String(tagId));
  }
  params.set('page', String(page));
  params.set('page_size', String(pageSize));
  params.set('sort', sort);

  return fetchJSON('/notes/search?' + params.toString());
}

async function fetchTags() {
  return fetchJSON('/tags/');
}

async function attachTagToNote(noteId, tagId) {
  return fetchJSON(`/notes/${noteId}/tags`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tag_id: tagId }),
  });
}

async function detachTagFromNote(noteId, tagId) {
  return fetchJSON(`/notes/${noteId}/tags/${tagId}`, {
    method: 'DELETE',
  });
}

function NotesSearchApp() {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [selectedTagId, setSelectedTagId] = useState(null);
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [sort, setSort] = useState('created_desc');
  const [results, setResults] = useState({ items: [], total: 0, page: 1, page_size: pageSize });
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reloadToken, setReloadToken] = useState(0);

  // Load tags on mount
  useEffect(() => {
    async function loadTags() {
      try {
        const tagList = await fetchTags();
        setTags(tagList);
      } catch (e) {
        console.error('Failed to load tags:', e);
      }
    }
    loadTags();
  }, []);

  // Listen for external events (e.g., note created) to refresh current search
  useEffect(() => {
    function handleChanged() {
      setReloadToken((t) => t + 1);
    }
    window.addEventListener('notes:changed', handleChanged);
    return () => window.removeEventListener('notes:changed', handleChanged);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function run() {
      setLoading(true);
      setError(null);
      try {
        const data = await searchNotes({
          q: submittedQuery,
          tagId: selectedTagId,
          page,
          pageSize,
          sort,
        });
        if (cancelled) return;
        setResults(data);
      } catch (e) {
        if (cancelled) return;
        setError(e && e.message ? e.message : 'Failed to load notes');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    run();

    return () => {
      cancelled = true;
    };
  }, [submittedQuery, selectedTagId, page, pageSize, sort, reloadToken]);

  const total = results.total || 0;
  const currentPage = results.page || page;
  const canPrev = currentPage > 1;
  const canNext = total > currentPage * pageSize;

  function onSubmitSearch(event) {
    event.preventDefault();
    setPage(1);
    setSubmittedQuery(query);
  }

  function onChangeSort(event) {
    const value = event.target.value;
    setPage(1);
    setSort(value);
  }

  function onChangeTagFilter(event) {
    const value = event.target.value;
    setPage(1);
    setSelectedTagId(value === '' ? null : parseInt(value, 10));
  }

  async function handleAttachTag(noteId, tagId) {
    try {
      await attachTagToNote(noteId, tagId);
      setReloadToken((t) => t + 1);
    } catch (e) {
      alert('Failed to attach tag: ' + (e.message || 'Unknown error'));
    }
  }

  async function handleDetachTag(noteId, tagId) {
    try {
      await detachTagFromNote(noteId, tagId);
      setReloadToken((t) => t + 1);
    } catch (e) {
      alert('Failed to detach tag: ' + (e.message || 'Unknown error'));
    }
  }

  function goPrev() {
    if (!canPrev) return;
    setPage((p) => Math.max(1, p - 1));
  }

  function goNext() {
    if (!canNext) return;
    setPage((p) => p + 1);
  }

  const handleRetry = () => {
    setSubmittedQuery((prev) => prev);
  };

  return (
    <div className="notes-search-react">
      {/* Search controls */}
      <form onSubmit={onSubmitSearch} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Search notes..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ flex: 1, minWidth: '200px', padding: '0.4rem' }}
        />
        <select value={selectedTagId || ''} onChange={onChangeTagFilter} style={{ padding: '0.4rem' }}>
          <option value="">All tags</option>
          {tags.map((tag) => (
            <option key={tag.id} value={tag.id}>
              {tag.name}
            </option>
          ))}
        </select>
        <select value={sort} onChange={onChangeSort} style={{ padding: '0.4rem' }}>
          <option value="created_desc">Newest first</option>
          <option value="title_asc">Title A–Z</option>
        </select>
        <button type="submit">Search</button>
      </form>

      {/* Status / count */}
      {loading && (
        <div className="status" style={{ fontStyle: 'italic' }}>
          Loading notes...
        </div>
      )}
      {error && (
        <div className="status error">
          Error: {error}{' '}
          <button type="button" onClick={handleRetry} style={{ marginLeft: '0.5rem' }}>
            Retry
          </button>
        </div>
      )}
      {!loading && !error && (
        <div className="status">
          {total === 0 ? 'No notes found' : `Found ${total} note${total === 1 ? '' : 's'}`}
          {total > 0 ? ` — Page ${currentPage}` : ''}
        </div>
      )}

      {/* Results list */}
      {!loading && !error && (
        <>
          {results.items.length === 0 && total === 0 ? (
            <div style={{ marginBottom: '0.5rem', fontStyle: 'italic' }}>
              Try adjusting your search query.
            </div>
          ) : (
            <ul style={{ paddingLeft: '1.25rem', listStyle: 'none' }}>
              {results.items.map((n) => (
                <li key={n.id || n.title + n.content} style={{ marginBottom: '1rem', padding: '0.5rem', border: '1px solid #eee', borderRadius: '4px' }}>
                  <div>
                    <strong>{n.title || '(no title)'}</strong>: {n.content}
                  </div>
                  <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                    {/* Display tags as chips */}
                    {n.tags && n.tags.length > 0 && (
                      <>
                        {n.tags.map((tag) => (
                          <span
                            key={tag.id}
                            style={{
                              display: 'inline-block',
                              padding: '0.2rem 0.5rem',
                              backgroundColor: '#e3f2fd',
                              color: '#1976d2',
                              borderRadius: '12px',
                              fontSize: '0.875rem',
                              cursor: 'pointer',
                            }}
                            onClick={() => handleDetachTag(n.id, tag.id)}
                            title="Click to remove tag"
                          >
                            {tag.name} ×
                          </span>
                        ))}
                      </>
                    )}
                    {/* Add tag dropdown */}
                    <select
                      value=""
                      onChange={(e) => {
                        const tagId = parseInt(e.target.value, 10);
                        if (tagId && !n.tags?.some((t) => t.id === tagId)) {
                          handleAttachTag(n.id, tagId);
                        }
                        e.target.value = '';
                      }}
                      style={{ padding: '0.2rem', fontSize: '0.875rem' }}
                    >
                      <option value="">+ Add tag</option>
                      {tags
                        .filter((tag) => !n.tags?.some((t) => t.id === tag.id))
                        .map((tag) => (
                          <option key={tag.id} value={tag.id}>
                            {tag.name}
                          </option>
                        ))}
                    </select>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </>
      )}

      {/* Pagination controls */}
      {!loading && !error && total > 0 && (
        <div className="pagination">
          <button type="button" onClick={goPrev} disabled={!canPrev}>
            Previous
          </button>
          <button type="button" onClick={goNext} disabled={!canNext}>
            Next
          </button>
          <span>
            Page {currentPage}, page size {pageSize}
          </span>
        </div>
      )}
    </div>
  );
}

export default NotesSearchApp;
