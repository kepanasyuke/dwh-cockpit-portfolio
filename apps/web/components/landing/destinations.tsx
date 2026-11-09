const PLACES = [
  { img: '/brand/tbilisi.jpg', city: 'Тбилиси', note: 'старый город и термы' },
  { img: '/brand/kamchatka.jpg', city: 'Камчатка', note: 'вулканы и океан' },
  { img: '/brand/kareliya.jpg', city: 'Карелия', note: 'озёра и леса' },
  { img: '/brand/murmansk.jpg', city: 'Мурманск', note: 'северное сияние' },
  { img: '/brand/bali.jpg', city: 'Бали', note: 'серфинг и рисовые террасы' },
  { img: '/brand/phuket.jpg', city: 'Пхукет', note: 'пляжи Андаманского моря' },
];

export const DestinationsSection = () => (
  <section id="destinations" style={{ marginBottom: 56 }}>
    <div className="section-head">
      <div>
        <h2>Направления, которые считает витрина</h2>
        <p>Каждая карточка — строка в витрине: брони, ADR, отмены и покрытие по направлению.</p>
      </div>
      <span className="tag tag-accent">фото с ostrovok.ru</span>
    </div>
    <div className="photo-grid">
      {PLACES.map((place) => (
        <figure className="photo-card" key={place.city}>
          <img src={place.img} alt={place.city} loading="lazy" />
          <figcaption>
            <b>{place.city}</b>
            <span>{place.note}</span>
          </figcaption>
        </figure>
      ))}
    </div>
  </section>
);
