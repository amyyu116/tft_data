import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import ProfileCard from './ProfileCard';
import MatchHistory from './MatchHistory';


const Profile = () => {
  const { gameName, tagLine } = useParams();
  const [playerData, setPlayerData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get(`http://localhost:3001/player/${gameName}/${tagLine}`)
      .then(res => {
        console.log(res.data);
        setPlayerData(res.data[0]);
      })
      .catch(err => {
        console.error(err);
        setError(err.message);
      });
  }, [gameName, tagLine]);

  if (error) return <div>Error: {error}</div>;
  if (!playerData) return <div>Loading...</div>;

  return (
    <div>
    <ProfileCard playerData={playerData} />
    <MatchHistory puuid={playerData.puuid} />
    </div>
  );
};

export default Profile;
