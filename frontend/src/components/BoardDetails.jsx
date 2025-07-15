import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TraitsList from './TraitsList';
import UnitList from './UnitList';

const BoardDetails = (props) => {
    const matchID = props.match_id;
    const puuid = props.puuid;
    const [boardData, setBoardData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
    axios
        .get(`http://localhost:3001/board/${puuid}/${matchID}`)
        .then(res => {
            setBoardData(res.data[0]);
        })
        .catch(err => {
            setError(err.message);
        });
    }, [puuid, matchID]);
    console.log(boardData);

    if (error) return <div>Error: {error}</div>;
    if (!boardData) return <div>Loading...</div>;

    return (
        <div>
            <TraitsList traits={boardData.traits} />
            <UnitList units={boardData.units} />
        </div>
    );
};

export default BoardDetails;
