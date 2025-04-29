function deleteNote(noteId) {
    const csrfToken = document.querySelector('input[name="csrf_token"]').value; // Get CSRF token from the DOM

    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId }),
        headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrfToken // Include CSRF token in the headers
        },
    }).then((_res) => {
        if (_res.ok) {
            window.location.href = "/";
        } else {
            console.error("Failed to delete note.");
        }
    }).catch((err) => {
        console.error("Error:", err);
    });
}