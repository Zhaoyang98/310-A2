import React from 'react';
import './Bubble.css';

const Bubble = (props: { message: string; sentByUser?: boolean }) => {
  return (
    <div className={`bubble-container ${props.sentByUser ? 'user' : ''}`}>
      <div className='bubble'>{props.message}</div>
    </div>
  );
};

export default Bubble;
