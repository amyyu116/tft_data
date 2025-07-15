import BoardDetails from './BoardDetails';

const MatchCard = (props) => {
  const matchData = props.match;

  if (!matchData) return <div>Loading...</div>;

  return (
    <div style={{ border: '1px solid gray', margin: '10px', padding: '10px' }}>
      {Object.entries(matchData).map(([key, value]) => (
        <div key={key}>
          <strong>{key}:</strong> {String(value)}
        </div>
      ))}
      <BoardDetails puuid={matchData.puuid} match_id={matchData.match_id} />
    </div>
  );
};

export default MatchCard;
