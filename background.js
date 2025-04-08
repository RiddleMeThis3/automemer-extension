chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
      id: "uploadMeme",
      title: "🛠️ Upload Image to Meme Machine",
      contexts: ["image"]
    });
  });
  
  chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "uploadMeme") {
      const imageUrl = info.srcUrl;
  
      fetch("https://automemer-extension.onrender.com/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ imageUrl })
      }).then(() => {
        console.log("✅ Meme sent to the machine!");
      }).catch((err) => {
        console.error("❌ Upload failed", err);
      });
    }
  });
  