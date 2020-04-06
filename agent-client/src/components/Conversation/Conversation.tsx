import React, { useState } from 'react';
import Bubble from '../Bubble/Bubble';
import axios from 'axios';
import './Conversation.css';

const API = 'https://cosc310-bot.herokuapp.com';
const INTRO = "Hello I'm Psych Agent Bot and I'm here to listen to you";

const Conversation = () => {
  const [hist, setHist] = useState<any>([]);
  const [message, setMessage] = useState<string | null | undefined>('');
  let messageRef: HTMLInputElement | null;

  const buildBubbles = () => {
    return hist.map((pair: any, i: any) => (
      <div key={i}>
        {pair[0] && <Bubble message={pair[0]} sentByUser={true} />}
        {pair[1] && <Bubble message={pair[1]} sentByUser={false} />}
      </div>
    ));
  };

  const pushToServer = (message: string) => {
    const url = `${API}/agent/${message}`;
    axios.post(url, hist).then((res) => {
      console.log(res.data);
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
      setHist([...hist, [message, null]]);
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
