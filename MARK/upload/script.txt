// Function to redirect to notes.html when '+' button is clicked
document.getElementById("add-note-btn").addEventListener("click", function() {
    window.location.href = "/add_note";
  });
  
  // Function to save note and redirect back to dashboard.html
  document.getElementById("save-note-btn").addEventListener("click", function() {
    // Get title and content values
    var title = document.getElementById("note-title").value;
    var content = document.getElementById("note-content").value;
  
    // Save to local storage or any other storage method you prefer
    localStorage.setItem(title, content);
  
    // Redirect back to dashboard.html
    window.location.href = "/dashboard";
  });
  
  // Function to display notes on dashboard.html
  window.onload = function() {
    var notesList = document.getElementById("notes-list");
    for (var i = 0; i < localStorage.length; i++) {
      var title = localStorage.key(i);
      var content = localStorage.getItem(title);
      var noteElement = document.createElement("div");
      noteElement.innerHTML = "<h3>" + title + "</h3><p>" + content + "</p>";
      notesList.appendChild(noteElement);
      // Add event listener to each note title to display content
      noteElement.addEventListener("click", function() {
        alert(content);
      });
    }
  };
  