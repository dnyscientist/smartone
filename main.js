
// Fetch and display RAG data
function fetchRagData() {
    fetch('/rags')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('ragDataBody');
            tableBody.innerHTML = '';
            data.forEach(item => {
                const row = `
                    <tr>
                        <td>${item.id}</td>
                        <td>${item.tag1}</td>
                        <td>${item.tag2}</td>
                        <td>${item.tag3}</td>
                        <td>${item.tag4}</td>
                        <td>${item.tag5}</td>
                        <td>${item.key}</td>
                        <td>${item.information}</td>
                        <td>${item.last_update}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="editRagData(${item.id})">Edit</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteRagData(${item.id})">Delete</button>
                        </td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });
        });
}

// Add new RAG data
function addRagData() {
    const formData = {
        tag1: document.getElementById('tag1').value,
        tag2: document.getElementById('tag2').value,
        tag3: document.getElementById('tag3').value,
        tag4: document.getElementById('tag4').value,
        tag5: document.getElementById('tag5').value,
        key: document.getElementById('key').value,
        information: document.getElementById('information').value
    };

    fetch('/rag', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        fetchRagData();
        document.getElementById('addForm').reset();
        bootstrap.Modal.getInstance(document.getElementById('addModal')).hide();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Populate edit modal with RAG data
function editRagData(id) {
    fetch(`/rag/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('editId').value = data.id;
            document.getElementById('editTag1').value = data.tag1;
            document.getElementById('editTag2').value = data.tag2;
            document.getElementById('editTag3').value = data.tag3;
            document.getElementById('editTag4').value = data.tag4;
            document.getElementById('editTag5').value = data.tag5;
            document.getElementById('editKey').value = data.key;
            document.getElementById('editInformation').value = data.information;
            
            const editModal = new bootstrap.Modal(document.getElementById('editModal'));
            editModal.show();
        });
}

// Update RAG data
function updateRagData() {
    const id = document.getElementById('editId').value;
    const formData = {
        tag1: document.getElementById('editTag1').value,
        tag2: document.getElementById('editTag2').value,
        tag3: document.getElementById('editTag3').value,
        tag4: document.getElementById('editTag4').value,
        tag5: document.getElementById('editTag5').value,
        key: document.getElementById('editKey').value,
        information: document.getElementById('editInformation').value
    };

    fetch(`/rag/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        fetchRagData();
        bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Delete RAG data
function deleteRagData(id) {
    if (confirm('Are you sure you want to delete this RAG data?')) {
        fetch(`/rag/${id}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            fetchRagData();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}

// Initial fetch of RAG data
fetchRagData();
