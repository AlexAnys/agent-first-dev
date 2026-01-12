import { useState, useEffect } from 'react';

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function ActionItemList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function loadActions() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchJSON('/action-items/');
      setItems(data);
    } catch (e) {
      setError(e && e.message ? e.message : 'Failed to load action items');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadActions();
    
    function handleChanged() {
      loadActions();
    }
    window.addEventListener('action-items:changed', handleChanged);
    return () => window.removeEventListener('action-items:changed', handleChanged);
  }, []);

  async function handleComplete(id) {
    try {
      await fetchJSON(`/action-items/${id}/complete`, { method: 'PUT' });
      loadActions();
    } catch (error) {
      console.error('Failed to complete action item:', error);
      alert('Failed to complete action item: ' + error.message);
    }
  }

  if (loading) {
    return <div>Loading action items...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <ul id="actions">
      {items.map((a) => (
        <li key={a.id}>
          {a.description} [{a.completed ? 'done' : 'open'}]
          {!a.completed && (
            <button onClick={() => handleComplete(a.id)}>Complete</button>
          )}
        </li>
      ))}
    </ul>
  );
}

export default ActionItemList;
