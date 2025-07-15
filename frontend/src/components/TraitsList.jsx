import TraitIcon from "./TraitIcon";
import traitData from "../data/tft-trait.json";

const TraitsList = ({ traits }) => {
    const tierMap = {
        1: "bronze",
        2: "silver",
        3: "gold",
        4: "prismatic"  
    };
	traits.sort(function(a, b) {
        if (a.tier_current < b.tier_current) return 1;
        if (a.tier_current > b.tier_current) return -1;
        return 0;
	});

    return (
        <div>
            {traits.map((trait) => {
                const traitInfo = traitData.data[trait.name];
                if (!traitInfo || trait.tier_current === 0) return null;

                return (
                <TraitIcon
                    key={trait.name}
                    iconSrc={`/trait/${traitInfo.image.full}`}
                    tier={tierMap[trait.tier_current]}
                />
                );
            })}
        </div>
    );
}

export default TraitsList;