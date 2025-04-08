chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
      id: "uploadMeme",
      title: "Upload Meme to Momo’s Meme TV",
      contexts: ["image"]
    });
  });
  
  chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    const imageUrl = info.srcUrl;
    const filename = imageUrl.split("/").pop();
  
    try {
      // Attempt direct fetch to bypass CORS if possible
      const response = await fetch(imageUrl);
      const blob = await response.blob();
  
      const formData = new FormData();
      formData.append("image", blob, filename);
  
      const uploadResponse = await fetch("https://automemer-extension.onrender.com/upload", {
        method: "POST",
        body: formData
      });
  
      if (!uploadResponse.ok) throw new Error("Direct upload failed");
  
      const result = await uploadResponse.json();
      console.log("✅ Meme uploaded directly:", result.url);
    } catch (err) {
      console.warn("⚠️ Direct upload failed. Falling back to URL upload…", err);
  
      try {
        const fallbackResponse = await fetch("https://automemer-extension.onrender.com/upload-url", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ url: imageUrl })
        });
  
        if (!fallbackResponse.ok) throw new Error("Fallback upload failed");
  
        const fallbackResult = await fallbackResponse.json();
        console.log("✅ Meme uploaded via fallback:", fallbackResult.url);
      } catch (fallbackErr) {
        console.error("❌ Both upload attempts failed:", fallbackErr);
      }
    }
  });
  