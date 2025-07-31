import { useRef, useState } from "react";
import "./MessageBox.css";

function MessageBox({ inputRef, sendMessage, enabled, messageText, setMessageText }) {

  const sendMessageAction = () => {
    if (!enabled) return;

    const message = messageText.trim();
    setMessageText("");
    
    if (message == "") return;

    sendMessage(message);
  };

  return (
    <div id="message-box-container">
      <input
        type="text"
        id="message-box"
        placeholder="Message"
        ref={inputRef}
        value={messageText}
        onChange={(e) => setMessageText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key == "Enter") sendMessageAction();
        }}
      />

      <button id="send-button" onClick={() => { sendMessageAction(); inputRef.current?.focus() }} disabled={!enabled}>ASK</button>
    </div>
  );
}

export default MessageBox;
