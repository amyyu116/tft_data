const UnitIcon = ({ w, h, imgSrc }) => {

    return (
    <div
      style={{
        width: w,
        height: h,
        backgroundImage: `url(${imgSrc})`,
        display: 'inline-block',

      }}
    />
  );
};

export default UnitIcon;