/*
  Basic behavior tests for NotesSearchApp using React Testing Library.
  These focus on the search parameters and pagination controls.
*/

const React = require('react');
const { render, screen, fireEvent, waitFor } = require('@testing-library/react');

// Ensure the global React used inside app.js is available
global.React = React;

const { NotesSearchApp } = require('../app.js');

function mockSearchResponse({ items = [], total = 0, page = 1, page_size = 10 } = {}) {
  return {
    ok: true,
    json: async () => ({ items, total, page, page_size }),
    text: async () => JSON.stringify({ items, total, page, page_size }),
  };
}

describe('NotesSearchApp', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test('initial render calls /notes/search with default pagination and sort', async () => {
    global.fetch.mockResolvedValueOnce(
      mockSearchResponse({ items: [], total: 0, page: 1, page_size: 10 })
    );

    render(React.createElement(NotesSearchApp));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    const url = global.fetch.mock.calls[0][0];
    expect(url).toContain('/notes/search?');
    expect(url).toContain('page=1');
    expect(url).toContain('page_size=10');
    expect(url).toContain('sort=created_desc');
  });

  test('submitting a search uses query and resets page to 1', async () => {
    // First call: initial load
    global.fetch.mockResolvedValueOnce(
      mockSearchResponse({ items: [], total: 0, page: 1, page_size: 10 })
    );
    // Second call: after submitting search
    global.fetch.mockResolvedValueOnce(
      mockSearchResponse({ items: [], total: 3, page: 1, page_size: 10 })
    );

    render(React.createElement(NotesSearchApp));

    // Wait for initial load
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    const input = screen.getByPlaceholderText('Search notes...');
    const button = screen.getByRole('button', { name: /search/i });

    fireEvent.change(input, { target: { value: 'meeting' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    const url = global.fetch.mock.calls[1][0];
    expect(url).toContain('/notes/search?');
    expect(url).toContain('q=meeting');
    expect(url).toContain('page=1');
    expect(url).toContain('page_size=10');
  });

  test('pagination buttons respect boundaries', async () => {
    const makeItems = (count) =>
      Array.from({ length: count }, (_, i) => ({ title: `Note ${i + 1}`, content: 'Body' }));

    // Initial load: page 1, total 15, page_size 10 (so has next page)
    global.fetch.mockResolvedValueOnce(
      mockSearchResponse({ items: makeItems(10), total: 15, page: 1, page_size: 10 })
    );
    // Page 2 load: no next page
    global.fetch.mockResolvedValueOnce(
      mockSearchResponse({ items: makeItems(5), total: 15, page: 2, page_size: 10 })
    );

    render(React.createElement(NotesSearchApp));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    let prevButton = screen.getByRole('button', { name: /previous/i });
    let nextButton = screen.getByRole('button', { name: /next/i });

    // On page 1: prev disabled, next enabled
    expect(prevButton).toBeDisabled();
    expect(nextButton).not.toBeDisabled();

    // Click next to go to page 2
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    // After going to page 2: prev enabled, next disabled (15 total, page_size 10)
    await waitFor(() => {
      const prevAfter = screen.getByRole('button', { name: /previous/i });
      const nextAfter = screen.getByRole('button', { name: /next/i });
      expect(prevAfter).not.toBeDisabled();
      expect(nextAfter).toBeDisabled();
    });
  });

  test('shows error state when fetch fails', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      text: async () => 'Internal error',
    });

    render(React.createElement(NotesSearchApp));

    await waitFor(() => {
      expect(screen.getByText(/error:/i)).toBeInTheDocument();
      expect(screen.getByText(/internal error/i)).toBeInTheDocument();
    });
  });

  test('displays empty state when there are no results', async () => {
    global.fetch.mockResolvedValueOnce(
      mockSearchResponse({ items: [], total: 0, page: 1, page_size: 10 })
    );

    render(React.createElement(NotesSearchApp));

    await waitFor(() => {
      expect(screen.getByText(/no notes found/i)).toBeInTheDocument();
      expect(screen.getByText(/try adjusting your search query/i)).toBeInTheDocument();
    });
  });

  test('changing sort sends correct sort parameter', async () => {
    // Initial load
    global.fetch.mockResolvedValueOnce(
      mockSearchResponse({ items: [], total: 0, page: 1, page_size: 10 })
    );
    // After sort change
    global.fetch.mockResolvedValueOnce(
      mockSearchResponse({ items: [], total: 0, page: 1, page_size: 10 })
    );

    render(React.createElement(NotesSearchApp));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    const sortSelect = screen.getByDisplayValue('Newest first');
    fireEvent.change(sortSelect, { target: { value: 'title_asc' } });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    const url = global.fetch.mock.calls[1][0];
    expect(url).toContain('sort=title_asc');
  });

  test('reacts to notes:changed event by refetching', async () => {
    // Initial load
    global.fetch.mockResolvedValueOnce(
      mockSearchResponse({ items: [], total: 1, page: 1, page_size: 10 })
    );
    // After notes:changed
    global.fetch.mockResolvedValueOnce(
      mockSearchResponse({ items: [], total: 2, page: 1, page_size: 10 })
    );

    render(React.createElement(NotesSearchApp));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    // Dispatch the custom event to trigger reload
    window.dispatchEvent(new Event('notes:changed'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });
});
