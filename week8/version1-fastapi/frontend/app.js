async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadNotes(params = {}) {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const query = new URLSearchParams(params);
  const notes = await fetchJSON('/notes/?' + query.toString());
  for (const n of notes) {
    const li = document.createElement('li');
    li.style.display = 'flex';
    li.style.flexDirection = 'column';
    li.style.gap = '0.5rem';
    li.style.marginBottom = '0.5rem';
    li.style.padding = '0.75rem';
    li.style.border = '1px solid #eee';
    li.style.borderRadius = '4px';
    li.style.background = '#fafafa';
    
    const header = document.createElement('div');
    header.style.display = 'flex';
    header.style.gap = '0.5rem';
    header.style.alignItems = 'center';
    
    const titleSpan = document.createElement('strong');
    titleSpan.textContent = n.title;
    titleSpan.style.flex = '1';
    header.appendChild(titleSpan);
    
    if (n.category) {
      const categoryBadge = document.createElement('span');
      categoryBadge.textContent = `📁 ${n.category.name}`;
      categoryBadge.style.background = '#e3f2fd';
      categoryBadge.style.padding = '0.25rem 0.5rem';
      categoryBadge.style.borderRadius = '4px';
      categoryBadge.style.fontSize = '0.85em';
      categoryBadge.style.cursor = 'pointer';
      categoryBadge.onclick = () => {
        document.getElementById('filter-category').value = n.category.id;
        applyFilters();
      };
      header.appendChild(categoryBadge);
    }
    
    if (n.tags && n.tags.length > 0) {
      const tagsContainer = document.createElement('div');
      tagsContainer.style.display = 'flex';
      tagsContainer.style.gap = '0.25rem';
      tagsContainer.style.flexWrap = 'wrap';
      for (const tag of n.tags) {
        const tagBadge = document.createElement('span');
        tagBadge.textContent = tag.name;
        tagBadge.style.background = tag.color || '#f0f0f0';
        tagBadge.style.color = '#333';
        tagBadge.style.padding = '0.15rem 0.4rem';
        tagBadge.style.borderRadius = '3px';
        tagBadge.style.fontSize = '0.8em';
        tagBadge.style.cursor = 'pointer';
        tagBadge.onclick = () => {
          document.getElementById('filter-tag').value = tag.id;
          applyFilters();
        };
        tagsContainer.appendChild(tagBadge);
      }
      header.appendChild(tagsContainer);
    }
    
    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = () => editNote(n);
    header.appendChild(editBtn);
    
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.style.background = '#dc3545';
    deleteBtn.style.color = 'white';
    deleteBtn.style.border = 'none';
    deleteBtn.onclick = async () => {
      if (confirm(`Delete note "${n.title}"?`)) {
        await fetchJSON(`/notes/${n.id}`, { method: 'DELETE' });
        loadNotes(params);
      }
    };
    header.appendChild(deleteBtn);
    
    li.appendChild(header);
    
    const contentSpan = document.createElement('div');
    contentSpan.textContent = n.content;
    contentSpan.style.color = '#555';
    li.appendChild(contentSpan);
    
    if (n.action_items && n.action_items.length > 0) {
      const actionsSpan = document.createElement('div');
      actionsSpan.style.fontSize = '0.85em';
      actionsSpan.style.color = '#888';
      actionsSpan.textContent = `📋 ${n.action_items.length} action item(s)`;
      li.appendChild(actionsSpan);
    }
    
    list.appendChild(li);
  }
}

async function loadActions(params = {}) {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const query = new URLSearchParams(params);
  const items = await fetchJSON('/action-items/?' + query.toString());
  for (const a of items) {
    const li = document.createElement('li');
    li.style.display = 'flex';
    li.style.gap = '0.5rem';
    li.style.alignItems = 'center';
    li.style.marginBottom = '0.5rem';
    
    const textContainer = document.createElement('div');
    textContainer.style.display = 'flex';
    textContainer.style.flexDirection = 'column';
    textContainer.style.gap = '0.25rem';
    textContainer.style.flex = '1';
    
    const textSpan = document.createElement('span');
    textSpan.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    textSpan.style.textDecoration = a.completed ? 'line-through' : 'none';
    textSpan.style.opacity = a.completed ? '0.6' : '1';
    textContainer.appendChild(textSpan);
    
    if (a.note_id) {
      const noteBadge = document.createElement('span');
      noteBadge.textContent = `📝 Note #${a.note_id}`;
      noteBadge.style.fontSize = '0.85em';
      noteBadge.style.color = '#666';
      noteBadge.style.cursor = 'pointer';
      noteBadge.onclick = async () => {
        const note = await fetchJSON(`/notes/${a.note_id}`);
        alert(`Note: ${note.title}\n${note.content}`);
      };
      textContainer.appendChild(noteBadge);
    }
    
    li.appendChild(textContainer);
    
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions(params);
      };
      li.appendChild(btn);
    } else {
      const btn = document.createElement('button');
      btn.textContent = 'Reopen';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ completed: false }),
        });
        loadActions(params);
      };
      li.appendChild(btn);
    }
    
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.style.background = '#dc3545';
    deleteBtn.style.color = 'white';
    deleteBtn.style.border = 'none';
    deleteBtn.onclick = async () => {
      if (confirm(`Delete action item "${a.description}"?`)) {
        await fetchJSON(`/action-items/${a.id}`, { method: 'DELETE' });
        loadActions(params);
      }
    };
    li.appendChild(deleteBtn);
    
    list.appendChild(li);
  }
}

let allCategories = [];
let allTags = [];
let allNotes = [];
let currentNoteFilters = {};

async function loadCategoriesForSelect() {
  allCategories = await fetchJSON('/categories/');
  const categorySelect = document.getElementById('note-category');
  const filterCategorySelect = document.getElementById('filter-category');
  
  // Clear existing options except first one
  categorySelect.innerHTML = '<option value="">No Category</option>';
  filterCategorySelect.innerHTML = '<option value="">All</option>';
  
  for (const cat of allCategories) {
    const option = document.createElement('option');
    option.value = cat.id;
    option.textContent = cat.name;
    categorySelect.appendChild(option);
    
    const filterOption = document.createElement('option');
    filterOption.value = cat.id;
    filterOption.textContent = cat.name;
    filterCategorySelect.appendChild(filterOption);
  }
}

async function loadTagsForSelect() {
  allTags = await fetchJSON('/tags/');
  const tagsContainer = document.getElementById('note-tags-list');
  const filterTagSelect = document.getElementById('filter-tag');
  
  tagsContainer.innerHTML = '';
  filterTagSelect.innerHTML = '<option value="">All</option>';
  
  for (const tag of allTags) {
    const label = document.createElement('label');
    label.style.display = 'flex';
    label.style.alignItems = 'center';
    label.style.gap = '0.25rem';
    label.style.fontSize = '0.9em';
    label.style.cursor = 'pointer';
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = tag.id;
    checkbox.id = `tag-checkbox-${tag.id}`;
    label.appendChild(checkbox);
    
    const colorBox = document.createElement('span');
    colorBox.style.width = '12px';
    colorBox.style.height = '12px';
    colorBox.style.borderRadius = '2px';
    colorBox.style.border = '1px solid #ccc';
    colorBox.style.background = tag.color || '#ccc';
    colorBox.style.display = 'inline-block';
    label.appendChild(colorBox);
    
    const nameSpan = document.createElement('span');
    nameSpan.textContent = tag.name;
    label.appendChild(nameSpan);
    
    tagsContainer.appendChild(label);
    
    const filterOption = document.createElement('option');
    filterOption.value = tag.id;
    filterOption.textContent = tag.name;
    filterTagSelect.appendChild(filterOption);
  }
}

async function loadNotesForSelect() {
  allNotes = await fetchJSON('/notes/');
  const noteSelect = document.getElementById('action-note');
  noteSelect.innerHTML = '<option value="">No Note</option>';
  
  for (const note of allNotes) {
    const option = document.createElement('option');
    option.value = note.id;
    option.textContent = note.title;
    noteSelect.appendChild(option);
  }
}

function applyFilters() {
  const categoryId = document.getElementById('filter-category').value;
  const tagId = document.getElementById('filter-tag').value;
  const searchQuery = document.getElementById('note-search').value;
  
  const params = {};
  if (searchQuery) params.q = searchQuery;
  if (categoryId) params.category_id = categoryId;
  if (tagId) params.tag_id = tagId;
  
  currentNoteFilters = params;
  loadNotes(params);
}

window.addEventListener('DOMContentLoaded', () => {
  // Load dropdowns first
  loadCategoriesForSelect();
  loadTagsForSelect();
  loadNotesForSelect();
  
  createNoteHandler = async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    const categoryId = document.getElementById('note-category').value;
    const selectedTags = Array.from(document.querySelectorAll('#note-tags-list input[type="checkbox"]:checked'))
      .map(cb => parseInt(cb.value));
    
    const payload = { title, content };
    if (categoryId) payload.category_id = parseInt(categoryId);
    if (selectedTags.length > 0) payload.tag_ids = selectedTags;
    
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    e.target.reset();
    document.getElementById('note-category').value = '';
    document.querySelectorAll('#note-tags-list input[type="checkbox"]').forEach(cb => cb.checked = false);
    loadNotes();
    loadNotesForSelect();
  };
  
  document.getElementById('note-form').addEventListener('submit', createNoteHandler);
  
  document.getElementById('filter-category').addEventListener('change', applyFilters);
  document.getElementById('filter-tag').addEventListener('change', applyFilters);
  
  document.getElementById('note-filter-clear').addEventListener('click', () => {
    document.getElementById('note-search').value = '';
    document.getElementById('filter-category').value = '';
    document.getElementById('filter-tag').value = '';
    currentNoteFilters = {};
    loadNotes();
  });

  document.getElementById('note-search-btn').addEventListener('click', applyFilters);
  
  document.getElementById('note-search').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      applyFilters();
    }
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    const noteId = document.getElementById('action-note').value;
    
    const payload = { description };
    if (noteId) payload.note_id = parseInt(noteId);
    
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    e.target.reset();
    document.getElementById('action-note').value = '';
    loadActions();
    loadNotesForSelect();
  });

  document.getElementById('filter-completed').addEventListener('change', (e) => {
    const checked = e.target.checked;
    loadActions({ completed: checked });
  });

  document.getElementById('tag-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('tag-name').value;
    const color = document.getElementById('tag-color').value;
    await fetchJSON('/tags/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, color: color || undefined }),
    });
    e.target.reset();
    loadTags();
    loadTagsForSelect();
  });

  document.getElementById('category-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('category-name').value;
    const description = document.getElementById('category-description').value;
    await fetchJSON('/categories/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description: description || undefined }),
    });
    e.target.reset();
    loadCategories();
    loadCategoriesForSelect();
  });

  loadNotes();
  loadActions();
  loadTags();
  loadCategories();
});

function editNote(note) {
  // Populate form with note data
  document.getElementById('note-title').value = note.title;
  document.getElementById('note-content').value = note.content;
  const categoryId = note.category_id || (note.category && note.category.id) || '';
  document.getElementById('note-category').value = categoryId;
  
  // Check tags
  document.querySelectorAll('#note-tags-list input[type="checkbox"]').forEach(cb => {
    cb.checked = note.tags && note.tags.some(t => t.id === parseInt(cb.value));
  });
  
  // Change form submit handler to update instead of create
  const form = document.getElementById('note-form');
  const newHandler = async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    const categoryId = document.getElementById('note-category').value;
    const selectedTags = Array.from(document.querySelectorAll('#note-tags-list input[type="checkbox"]:checked'))
      .map(cb => parseInt(cb.value));
    
    const payload = { title, content };
    if (categoryId) payload.category_id = parseInt(categoryId);
    else payload.category_id = 0; // Clear category
    payload.tag_ids = selectedTags;
    
    await fetchJSON(`/notes/${note.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    e.target.reset();
    document.getElementById('note-category').value = '';
    document.querySelectorAll('#note-tags-list input[type="checkbox"]').forEach(cb => cb.checked = false);
    form.removeEventListener('submit', newHandler);
    form.addEventListener('submit', createNoteHandler);
    loadNotes(currentNoteFilters);
    loadNotesForSelect();
  };
  
  // Remove old handler and add new one
  form.removeEventListener('submit', createNoteHandler);
  form.addEventListener('submit', newHandler);
  
  // Scroll to form
  document.getElementById('note-form').scrollIntoView({ behavior: 'smooth' });
}

let createNoteHandler;

async function loadTags() {
  const list = document.getElementById('tags');
  list.innerHTML = '';
  const tags = await fetchJSON('/tags/');
  for (const t of tags) {
    const li = document.createElement('li');
    li.style.display = 'flex';
    li.style.gap = '0.5rem';
    li.style.alignItems = 'center';
    li.style.marginBottom = '0.5rem';
    
    const colorBox = document.createElement('span');
    colorBox.style.width = '20px';
    colorBox.style.height = '20px';
    colorBox.style.borderRadius = '4px';
    colorBox.style.border = '1px solid #ccc';
    colorBox.style.background = t.color || '#ccc';
    colorBox.style.display = 'inline-block';
    li.appendChild(colorBox);
    
    const textSpan = document.createElement('span');
    textSpan.textContent = t.name;
    textSpan.style.flex = '1';
    li.appendChild(textSpan);
    
    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = () => {
      const newName = prompt('Enter new tag name:', t.name);
      const newColor = prompt('Enter new color (e.g., #FF0000):', t.color || '');
      if (newName && newName !== t.name) {
        fetchJSON(`/tags/${t.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: newName, color: newColor || undefined }),
        }).then(() => loadTags());
      } else if (newColor && newColor !== t.color) {
        fetchJSON(`/tags/${t.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ color: newColor }),
        }).then(() => loadTags());
      }
    };
    li.appendChild(editBtn);
    
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.style.background = '#dc3545';
    deleteBtn.style.color = 'white';
    deleteBtn.style.border = 'none';
    deleteBtn.onclick = async () => {
      if (confirm(`Delete tag "${t.name}"?`)) {
        await fetchJSON(`/tags/${t.id}`, { method: 'DELETE' });
        loadTags();
      }
    };
    li.appendChild(deleteBtn);
    
    list.appendChild(li);
  }
}

async function loadCategories() {
  const list = document.getElementById('categories');
  list.innerHTML = '';
  const categories = await fetchJSON('/categories/');
  for (const c of categories) {
    const li = document.createElement('li');
    li.style.display = 'flex';
    li.style.flexDirection = 'column';
    li.style.gap = '0.5rem';
    li.style.marginBottom = '0.5rem';
    li.style.padding = '0.5rem';
    li.style.border = '1px solid #eee';
    li.style.borderRadius = '4px';
    
    const header = document.createElement('div');
    header.style.display = 'flex';
    header.style.gap = '0.5rem';
    header.style.alignItems = 'center';
    
    const nameSpan = document.createElement('strong');
    nameSpan.textContent = c.name;
    nameSpan.style.flex = '1';
    header.appendChild(nameSpan);
    
    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = () => {
      const newName = prompt('Enter new category name:', c.name);
      const newDesc = prompt('Enter new description:', c.description || '');
      if (newName !== null && (newName !== c.name || newDesc !== (c.description || ''))) {
        fetchJSON(`/categories/${c.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            name: newName || undefined,
            description: newDesc || undefined 
          }),
        }).then(() => loadCategories());
      }
    };
    header.appendChild(editBtn);
    
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.style.background = '#dc3545';
    deleteBtn.style.color = 'white';
    deleteBtn.style.border = 'none';
    deleteBtn.onclick = async () => {
      if (confirm(`Delete category "${c.name}"?`)) {
        await fetchJSON(`/categories/${c.id}`, { method: 'DELETE' });
        loadCategories();
      }
    };
    header.appendChild(deleteBtn);
    
    li.appendChild(header);
    
    if (c.description) {
      const descSpan = document.createElement('span');
      descSpan.textContent = c.description;
      descSpan.style.color = '#666';
      descSpan.style.fontSize = '0.9em';
      li.appendChild(descSpan);
    }
    
    list.appendChild(li);
  }
}


