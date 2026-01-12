import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import NoteForm from '../src/components/NoteForm';

function mockFetchResponse(ok = true, data = {}) {
  return {
    ok,
    json: async () => data,
    text: async () => JSON.stringify(data),
  };
}

describe('NoteForm', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    window.dispatchEvent = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test('submits note with title and content', async () => {
    global.fetch.mockResolvedValueOnce(mockFetchResponse(true, { id: 1, title: 'Test', content: 'Content' }));

    render(<NoteForm />);

    const titleInput = screen.getByPlaceholderText('Title');
    const contentInput = screen.getByPlaceholderText('Content');
    const submitButton = screen.getByRole('button', { name: /add/i });

    fireEvent.change(titleInput, { target: { value: 'Test Note' } });
    fireEvent.change(contentInput, { target: { value: 'Test Content' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/notes/',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: 'Test Note', content: 'Test Content' }),
        })
      );
    });

    expect(titleInput.value).toBe('');
    expect(contentInput.value).toBe('');
    expect(window.dispatchEvent).toHaveBeenCalledWith(expect.any(Event));
  });

  test('shows error alert when submission fails', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      text: async () => 'Error message',
    });
    global.alert = jest.fn();

    render(<NoteForm />);

    const titleInput = screen.getByPlaceholderText('Title');
    const contentInput = screen.getByPlaceholderText('Content');
    const submitButton = screen.getByRole('button', { name: /add/i });

    fireEvent.change(titleInput, { target: { value: 'Test' } });
    fireEvent.change(contentInput, { target: { value: 'Content' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith(expect.stringContaining('Failed to create note'));
    });
  });
});
