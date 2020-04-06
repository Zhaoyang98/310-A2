import React, { useState } from 'react';
import Bubble from '../Bubble/Bubble';
import axios from 'axios';
import './Conversation.css';

const API = 'https://cosc310-bot.herokuapp.com';
const INTRO = "Hello I'm Psych Agent Bot and I'm here to listen to you";

const Conversation = () => {
  const [hist, setHist] = useState<string[]>([]);
  const [message, setMessage] = useState<string | null | undefined>('');
  let messageRef: HTMLInputElement | null;

  const buildBubbles = () => {
    return [INTRO, ...hist].map((value, i) => (
      <Bubble key={i} message={value} sentByUser={i % 2 !== 0} />
    ));
  };

  const pushToServer = (message: string) => {
    const url = `${API}/agent/${message}`;
    axios.post(url, hist).then((res) => {
      setHist(res.data);
      scroll();
    });
  };

  const scroll = () => {
    const div = document.getElementById('scroll');
    if (div) {
      div.scrollTop = div.scrollHeight;
    }
  };

  const onAddMessage = (e: any) => {
    if (message) {
      setHist([...hist, message]);
      pushToServer(message);
      scroll();
      setMessage('');
    }
  };

  return (
    <div className='conversation'>
      <div className='bubbles' id='scroll'>
        {buildBubbles()}
      </div>
      <div className='input' id='input'>
        <input
          onChange={(e) => setMessage(e.target.value)}
          value={message ?? ''}
        />
        <button onClick={onAddMessage}>Send</button>
      </div>
    </div>
  );
};

export default Conversation;
