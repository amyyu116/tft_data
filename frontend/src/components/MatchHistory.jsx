import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MatchCard from './MatchCard';

const MatchHistory = (props) => {
  const puuid = props.puuid;
  const [matchData, setMatchData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get(`http://localhost:3001/match_history/${puuid}`)
      .then(res => {
        setMatchData(res.data);
      })
      .catch(err => {
        console.error(err);
        setError(err.message);
      });
  }, [puuid]);

  if (error) return <div>Error: {error}</div>;
  if (!matchData) return <div>Loading...</div>;

  return (
    <div>
      {matchData.map((match, index) => (
        <MatchCard key={index} match={match} />
      ))}
    </div>
  );
};

export default MatchHistory;
