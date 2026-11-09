const PLACES = [
  { img: '/brand/tbilisi.jpg', city: 'Тбилиси' },
  { img: '/brand/kamchatka.jpg', city: 'Камчатка' },
  { img: '/brand/kareliya.jpg', city: 'Карелия' },
  { img: '/brand/murmansk.jpg', city: 'Мурманск' },
  { img: '/brand/bali.jpg', city: 'Бали' },
  { img: '/brand/phuket.jpg', city: 'Пхукет' },
];

export const PhotoStrip = () => (
  <div className="photo-strip">
    {PLACES.map((place) => (
      <figure className="photo-tile" key={place.city}>
        <img src={place.img} alt={place.city} loading="lazy" />
        <figcaption>{place.city}</figcaption>
      </figure>
    ))}
  </div>
);
