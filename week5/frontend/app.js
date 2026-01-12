async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// --- Notes search API helper using /notes/search ---
async function searchNotes({ q = '', page = 1, pageSize = 10, sort = 'created_desc' } = {}) {
  const params = new URLSearchParams();
  if (q && q.trim()) {
    params.set('q', q.trim());
  }
  params.set('page', String(page));
  params.set('page_size', String(pageSize));
  params.set('sort', sort);

  // Expecting envelope: { items, total, page, page_size }
  return fetchJSON('/notes/search?' + params.toString());
}

async function loadActions() {
  const list = document.getElementById('actions');
  if (!list) return;
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

// --- React notes search UI ---
function NotesSearchApp() {
  const { useState, useEffect } = React;

  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [sort, setSort] = useState('created_desc');
  const [results, setResults] = useState({ items: [], total: 0, page: 1, page_size: pageSize });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reloadToken, setReloadToken] = useState(0);

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
  }, [submittedQuery, page, pageSize, sort, reloadToken]);

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

  function goPrev() {
    if (!canPrev) return;
    setPage((p) => Math.max(1, p - 1));
  }

  function goNext() {
    if (!canNext) return;
    setPage((p) => p + 1);
  }

  const handleRetry = () => {
    // Re-trigger effect with same dependencies
    setSubmittedQuery((prev) => prev);
  };

  const children = [];

  // Search controls
  children.push(
    React.createElement(
      'form',
      { key: 'search-form', onSubmit: onSubmitSearch, style: { display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' } },
      React.createElement('input', {
        type: 'text',
        placeholder: 'Search notes...',
        value: query,
        onChange: (e) => setQuery(e.target.value),
        style: { flex: 1, padding: '0.4rem' },
      }),
      React.createElement(
        'select',
        {
          value: sort,
          onChange: onChangeSort,
        },
        React.createElement('option', { value: 'created_desc' }, 'Newest first'),
        React.createElement('option', { value: 'title_asc' }, 'Title A–Z')
      ),
      React.createElement('button', { type: 'submit' }, 'Search')
    )
  );

  // Status / count
  if (loading) {
    children.push(
      React.createElement(
        'div',
        { key: 'status-loading', className: 'status', style: { fontStyle: 'italic' } },
        'Loading notes...'
      )
    );
  } else if (error) {
    children.push(
      React.createElement(
        'div',
        { key: 'status-error', className: 'status error' },
        'Error: ',
        error,
        ' ',
        React.createElement(
          'button',
          { type: 'button', onClick: handleRetry, style: { marginLeft: '0.5rem' } },
          'Retry'
        )
      )
    );
  } else {
    const label = total === 0 ? 'No notes found' : `Found ${total} note${total === 1 ? '' : 's'}`;
    children.push(
      React.createElement(
        'div',
        { key: 'status-info', className: 'status' },
        label,
        total > 0 ? ` f Page ${currentPage}` : ''
      )
    );
  }

  // Results list
  const items = results.items || [];
  if (!loading && !error) {
    if (items.length === 0 && total === 0) {
      children.push(
        React.createElement(
          'div',
          { key: 'empty', style: { marginBottom: '0.5rem', fontStyle: 'italic' } },
          'Try adjusting your search query.'
        )
      );
    } else {
      children.push(
        React.createElement(
          'ul',
          { key: 'results-list', style: { paddingLeft: '1.25rem' } },
          items.map(function (n) {
            return React.createElement(
              'li',
              { key: n.id || n.title + n.content },
              React.createElement('strong', null, n.title || '(no title)'),
              ': ',
              n.content
            );
          })
        )
      );
    }
  }

  // Pagination controls
  if (!loading && !error && total > 0) {
    children.push(
      React.createElement(
        'div',
        { key: 'pagination', className: 'pagination' },
        React.createElement(
          'button',
          { type: 'button', onClick: goPrev, disabled: !canPrev },
          'Previous'
        ),
        React.createElement(
          'button',
          { type: 'button', onClick: goNext, disabled: !canNext },
          'Next'
        ),
        React.createElement(
          'span',
          null,
          `Page ${currentPage}, page size ${pageSize}`
        )
      )
    );
  }

  return React.createElement('div', { className: 'notes-search-react' }, children);
}

function bootstrapReactNotes() {
  const rootEl = document.getElementById('notes-react-root');
  if (!rootEl || !window.React || !window.ReactDOM || !window.ReactDOM.createRoot) {
    return;
  }

  const root = ReactDOM.createRoot(rootEl);
  root.render(React.createElement(NotesSearchApp));
}

window.addEventListener('DOMContentLoaded', () => {
  const noteForm = document.getElementById('note-form');
  if (noteForm) {
    noteForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('note-title').value;
      const content = document.getElementById('note-content').value;
      await fetchJSON('/notes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      e.target.reset();
      // Inform React search UI that notes have changed so it can refresh
      window.dispatchEvent(new Event('notes:changed'));
    });
  }

  const actionForm = document.getElementById('action-form');
  if (actionForm) {
    actionForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const description = document.getElementById('action-desc').value;
      await fetchJSON('/action-items/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      e.target.reset();
      loadActions();
    });
  }

  // Notes are now rendered exclusively via the React search UI
  loadActions();
  bootstrapReactNotes();
});

// Export for Jest/Node tests (safe no-op in browser)
if (typeof module !== 'undefined') {
  module.exports = { NotesSearchApp };
}
