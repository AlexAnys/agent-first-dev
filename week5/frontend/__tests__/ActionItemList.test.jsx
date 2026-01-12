import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ActionItemList from '../src/components/ActionItemList';

function mockFetchResponse(ok = true, data = []) {
  return {
    ok,
    json: async () => data,
    text: async () => JSON.stringify(data),
  };
}

describe('ActionItemList', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test('loads and displays action items', async () => {
    const items = [
      { id: 1, description: 'Task 1', completed: false },
      { id: 2, description: 'Task 2', completed: true },
    ];
    global.fetch.mockResolvedValueOnce(mockFetchResponse(true, items));

    render(<ActionItemList />);

    await waitFor(() => {
      expect(screen.getByText(/task 1/i)).toBeInTheDocument();
      expect(screen.getByText(/task 2/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/done/i)).toBeInTheDocument();
    expect(screen.getByText(/open/i)).toBeInTheDocument();
  });

  test('shows loading state initially', () => {
    global.fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<ActionItemList />);

    expect(screen.getByText(/loading action items/i)).toBeInTheDocument();
  });

  test('shows error state when fetch fails', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      text: async () => 'Error message',
    });

    render(<ActionItemList />);

    await waitFor(() => {
      expect(screen.getByText(/error:/i)).toBeInTheDocument();
    });
  });

  test('completes action item when button clicked', async () => {
    const items = [{ id: 1, description: 'Task 1', completed: false }];
    global.fetch
      .mockResolvedValueOnce(mockFetchResponse(true, items)) // Initial load
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) }) // Complete request
      .mockResolvedValueOnce(mockFetchResponse(true, [{ ...items[0], completed: true }])); // Reload

    render(<ActionItemList />);

    await waitFor(() => {
      expect(screen.getByText(/task 1/i)).toBeInTheDocument();
    });

    const completeButton = screen.getByRole('button', { name: /complete/i });
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/action-items/1/complete',
        expect.objectContaining({ method: 'PUT' })
      );
    });
  });

  test('reloads when action-items:changed event is dispatched', async () => {
    const items1 = [{ id: 1, description: 'Task 1', completed: false }];
    const items2 = [{ id: 1, description: 'Task 1', completed: false }, { id: 2, description: 'Task 2', completed: false }];

    global.fetch
      .mockResolvedValueOnce(mockFetchResponse(true, items1))
      .mockResolvedValueOnce(mockFetchResponse(true, items2));

    render(<ActionItemList />);

    await waitFor(() => {
      expect(screen.getByText(/task 1/i)).toBeInTheDocument();
    });

    window.dispatchEvent(new Event('action-items:changed'));

    await waitFor(() => {
      expect(screen.getByText(/task 2/i)).toBeInTheDocument();
    });
  });
});
