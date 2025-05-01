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
            alert(data.message || 'Note deleted successfully!');
            window.location.href = '/';
        } else {
            alert(`Error: ${data.message || 'Failed to delete note.'}`);
        }
    })
    .catch(error => {
        console.error('Error deleting note:', error);
        alert('An error occurred while deleting the note. Please try again.');
    });
}