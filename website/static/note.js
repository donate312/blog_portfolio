function deleteNote(noteId) {
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;
    console.log('Deleting note:', noteId, 'CSRF Token:', csrfToken);

    fetch(`/delete-note/${noteId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.location.href = '/?flash=success&message=' + encodeURIComponent(data.message || 'Note deleted successfully');
        } else {
            window.location.href = '/?flash=error&message=' + encodeURIComponent(data.message || 'Failed to delete note');
        }
    })
    .catch(error => {
        console.error('Error deleting note:', error);
        window.location.href = '/?flash=error&message=' + encodeURIComponent('An error occurred while deleting the note');
    });
}