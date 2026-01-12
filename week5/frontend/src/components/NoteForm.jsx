import { useState } from 'react';

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function NoteForm() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      await fetchJSON('/notes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      setTitle('');
      setContent('');
      // Inform React search UI that notes have changed so it can refresh
      window.dispatchEvent(new Event('notes:changed'));
    } catch (error) {
      console.error('Failed to create note:', error);
      alert('Failed to create note: ' + error.message);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        id="note-title"
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <input
        id="note-content"
        placeholder="Content"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        required
      />
      <button type="submit">Add</button>
    </form>
  );
}

export default NoteForm;
