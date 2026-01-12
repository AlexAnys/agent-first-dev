import { useState } from 'react';

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function ActionItemForm() {
  const [description, setDescription] = useState('');

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      await fetchJSON('/action-items/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      setDescription('');
      // Trigger reload of action items list
      window.dispatchEvent(new Event('action-items:changed'));
    } catch (error) {
      console.error('Failed to create action item:', error);
      alert('Failed to create action item: ' + error.message);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        id="action-desc"
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
      />
      <button type="submit">Add</button>
    </form>
  );
}

export default ActionItemForm;
