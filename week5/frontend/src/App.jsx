import { useState, useEffect } from 'react';
import NotesSearchApp from './components/NotesSearchApp';
import NoteForm from './components/NoteForm';
import ActionItemForm from './components/ActionItemForm';
import ActionItemList from './components/ActionItemList';
import './App.css';

function App() {
  return (
    <main>
      <h1>Modern Software Dev Starter</h1>

      <section>
        <h2>Notes</h2>
        <NotesSearchApp />
        <NoteForm />
      </section>

      <section>
        <h2>Action Items</h2>
        <ActionItemForm />
        <ActionItemList />
      </section>
    </main>
  );
}

export default App;
