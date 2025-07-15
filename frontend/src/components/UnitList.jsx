import UnitIcon from "./UnitIcon";
import champData from "../data/tft-champion.json";

const UnitList = ({ units }) => {

	units.sort(function(a, b) {
        if (a.rarity < b.rarity) return 1;
        if (a.rarity > b.rarity) return -1;
        return 0;
	});

    return (
        <div>
            {units.map((unit) => {
                const unitInfo = champData.data[`Maps/Shipping/Map22/Sets/TFTSet14/Shop/${unit.character_id}`];
                if (!unitInfo) return null;
                console.log(`https://cdn.metatft.com/cdn-cgi/image/width=48,height=48,format=auto/https://cdn.metatft.com/file/metatft/champions/${encodeURIComponent(unit.character_id.toLowerCase())}.png`);
                return (
                <UnitIcon
                    key={unit.character_id}
                    imgSrc={`https://cdn.metatft.com/cdn-cgi/image/width=48,height=48,format=auto/https://cdn.metatft.com/file/metatft/champions/${encodeURIComponent(unit.character_id.toLowerCase())}.png`}
                    w={unitInfo.image.w}
                    h={unitInfo.image.h}
                />
                );
            })}
        </div>
    );
}

export default UnitList;