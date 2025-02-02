document.addEventListener("DOMContentLoaded", function() {
    const button = document.querySelector(".download-btn");
    
    button.addEventListener("click", function(event) {
        event.preventDefault();
        button.style.transform = "scale(0.9)";
        setTimeout(() => button.style.transform = "scale(1.1)", 150);
        setTimeout(() => button.style.transform = "scale(1)", 300);
        
        // Simulate download
        setTimeout(() => {
            window.location.href = button.getAttribute("href");
        }, 500);
    });
});
