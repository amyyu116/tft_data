const ProfileCard = (props) => {   
    const { playerData } = props;

    return (
    <div style={{margin:30}}>
        <h1>Player Info</h1>
        <img src={`/profileicon/${playerData.icon_id}.png`} alt="" style={{height: 160, width: 160, borderRadius: 160}}/>
        <h2>{playerData.game_name}#{playerData.tag_line}</h2>
        <p style={{fontSize: 18}}>lv. {playerData.summoner_level}</p>
    </div>
    );
};

export default ProfileCard;
