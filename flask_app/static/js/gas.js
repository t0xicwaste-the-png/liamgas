// =========================================================
// FAKE AD CONFIGURATION
// =========================================================

// 1. Choose how many popups you want to spawn (e.g., 5, 15, 50!)
const numberOfPopups = 500; 

// 2. Chance of a popup being a REAL Adsterra ad (0.0 to 1.0)
// 0.5 means half of them will be real monetized ads!
const chanceOfRealAd = 0.6;

// 3. Put your image names here
const fakeAdFiles = [
    "Untitled 03-13-2026 11-00-37.png",
    "everything.png",
    "anything.png"
];

// This converts the filenames into proper URLs for Flask
const fakeAds = fakeAdFiles.map(filename => "/static/images/" + filename);

function showAds() {
    // Hide the button
    document.getElementById('gas-btn').style.display = 'none';
    
    // Show the original center Adsterra ad
    document.getElementById('ad-container').style.display = 'block';

    const bodyWidth = window.innerWidth;
    const bodyHeight = window.innerHeight;

    // Loop through and spawn the number of popups you picked
    for (let i = 0; i < numberOfPopups; i++) {
        
        let isRealAd = Math.random() < chanceOfRealAd;
        let popupElement;
        let popupWidth;
        let popupHeight;

        if (isRealAd) {
            // Create a REAL Adsterra Ad inside an invisible iframe so it loads correctly
            popupElement = document.createElement("iframe");
            popupElement.className = "fake-ad";
            popupElement.style.border = "none";
            popupElement.style.overflow = "hidden";
            
            // Adsterra dimensions
            popupWidth = 300;
            popupHeight = 250;
            popupElement.style.width = popupWidth + "px";
            popupElement.style.height = popupHeight + "px";

            // Load the real ad snippet safely via a static HTML file
            popupElement.src = "/static/ad.html";
        } else {
            // Create a FAKE Image Ad
            popupElement = document.createElement("img");
            
            let randomImgSrc = fakeAds[Math.floor(Math.random() * fakeAds.length)];
            popupElement.src = randomImgSrc;
            popupElement.className = "fake-ad";
            
            // Random Size for fake ads
            popupWidth = Math.floor(Math.random() * 350) + 100;
            popupHeight = popupWidth; // rough approximation to keep it on screen
            popupElement.style.width = popupWidth + "px";
        }
        
        // Random X and Y position
        let randomX = Math.floor(Math.random() * (bodyWidth - popupWidth));
        let randomY = Math.floor(Math.random() * (bodyHeight - popupHeight));
        
        // Ensure they don't spawn off-screen
        popupElement.style.left = Math.max(0, randomX) + "px";
        popupElement.style.top = Math.max(0, randomY) + "px";

        // Very little rotation (between -4 and 4 degrees)
        let rotation = Math.floor(Math.random() * 8) - 4;
        popupElement.style.transform = `rotate(${rotation}deg)`;

        // Add a staggered delay before they instantly pop onto the screen!
        setTimeout(() => {
            document.body.appendChild(popupElement);
        }, i * 200 + 100); // 200ms delay between each popup
    }
}
