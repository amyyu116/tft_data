const TraitIcon = ({ iconSrc, tier }) => {
  const tierColors = {
    bronze: '#cd7f32',
    silver: '#c0c0c0',
    gold: '#ffd700',
    prismatic: '#b700ff',
  };

  return (
    <div
      style={{
        width: 48,
        height: 48,
        backgroundColor: tierColors[tier],
        WebkitMaskImage: `url(${iconSrc})`,
        maskImage: `url(${iconSrc})`,
        WebkitMaskSize: 'contain',
        maskSize: 'contain',
        WebkitMaskRepeat: 'no-repeat',
        maskRepeat: 'no-repeat',
        WebkitMaskPosition: 'center',
        maskPosition: 'center',
        display: 'inline-block',
      }}
    />
  );
};

export default TraitIcon;
