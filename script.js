// Function to Embed Message into Image
function embedMessage() {
    let fileInput = document.getElementById("uploadImage").files[0];
    let message = document.getElementById("secretMessage").value;
    
    if (!fileInput || message === "") {
        alert("Please select an image and enter a secret message!");
        return;
    }

    let reader = new FileReader();
    reader.onload = function (event) {
        let img = new Image();
        img.onload = function () {
            let canvas = document.getElementById("stegoCanvas");
            let ctx = canvas.getContext("2d");

            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);

            let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            let data = imageData.data;

            let binaryMessage = message.split("").map(char => char.charCodeAt(0).toString(2).padStart(8, '0')).join('');
            binaryMessage += "00000000"; // Null terminator

            if (binaryMessage.length > data.length / 4) {
                alert("Message too long for this image!");
                return;
            }

            for (let i = 0; i < binaryMessage.length; i++) {
                data[i * 4] = (data[i * 4] & 0xFE) | parseInt(binaryMessage[i]);
            }

            ctx.putImageData(imageData, 0, 0);
            let stegoURL = canvas.toDataURL("image/png");
            document.getElementById("downloadLink").href = stegoURL;
            document.getElementById("downloadLink").download = "stego_image.png";
            document.getElementById("downloadLink").classList.remove("hidden");
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(fileInput);
}

// Function to Extract Message from Image
function extractMessage() {
    let fileInput = document.getElementById("uploadStego").files[0];
    
    if (!fileInput) {
        alert("Please select a stego image!");
        return;
    }

    let reader = new FileReader();
    reader.onload = function (event) {
        let img = new Image();
        img.onload = function () {
            let canvas = document.createElement("canvas");
            let ctx = canvas.getContext("2d");

            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);

            let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            let data = imageData.data;

            let binaryMessage = "";
            for (let i = 0; i < data.length / 4; i++) {
                binaryMessage += (data[i * 4] & 1).toString();
            }

            let message = "";
            for (let i = 0; i < binaryMessage.length; i += 8) {
                let byte = binaryMessage.substring(i, i + 8);
                if (byte === "00000000") break;
                message += String.fromCharCode(parseInt(byte, 2));
            }

            document.getElementById("extractedMessage").innerText = "Extracted Message: " + message;
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(fileInput);
}
