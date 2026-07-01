function sendValue(value) {
  window.parent.postMessage(
    {
      isStreamlitMessage: true,
      type: "streamlit:setComponentValue",
      value: value
    },
    "*"
  );
}

const button = document.getElementById("test-button");
const result = document.getElementById("result");

button.addEventListener("click", function () {
  const isbn = "9780547928227";
  result.innerText = "Sent ISBN: " + isbn;
  sendValue(isbn);
});