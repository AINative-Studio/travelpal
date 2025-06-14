## 1. Users & Profiles

```sql
-- Core user account
CREATE TABLE users (
  user_id        UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  name           VARCHAR(100) NOT NULL,
  email          VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255),
  created_at     TIMESTAMP   NOT NULL DEFAULT now(),
  updated_at     TIMESTAMP   NOT NULL DEFAULT now()
);

-- Extended preferences & loyalty info
CREATE TABLE user_preferences (
  pref_id        UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  seat_class     VARCHAR(50),           -- e.g. "Economy", "Business"
  hotel_rating   INT CHECK (hotel_rating BETWEEN 1 AND 5),
  budget_min     NUMERIC(10,2),
  budget_max     NUMERIC(10,2),
  loyalty_numbers JSONB,               -- { "airline": "ABC123", "hotel": "XYZ789" }
  language       VARCHAR(10) DEFAULT 'en',
  timezone       VARCHAR(50)            -- e.g. "America/Los_Angeles"
);
```

---

## 2. Bookings & Line-Items

```sql
-- A generic booking record
CREATE TABLE bookings (
  booking_id     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  status         VARCHAR(20) NOT NULL CHECK (status IN ('pending','confirmed','cancelled')),
  total_price    NUMERIC(12,2) NOT NULL,
  currency       CHAR(3)     NOT NULL DEFAULT 'USD',
  created_at     TIMESTAMP   NOT NULL DEFAULT now(),
  updated_at     TIMESTAMP   NOT NULL DEFAULT now()
);

-- Polymorphic line-item to reference any booking subtype
CREATE TABLE booking_items (
  item_id        UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id     UUID        NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
  item_type      VARCHAR(20) NOT NULL CHECK (item_type IN ('flight','hotel','car','tour')),
  item_ref_id    UUID        NOT NULL     -- FK into the specific subtype table
);
```

---

### 2.1 Flight Bookings

```sql
CREATE TABLE flight_bookings (
  flight_id        UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  provider         VARCHAR(50) NOT NULL,   -- e.g. "Amadeus"
  booking_ref      UUID        NOT NULL,   -- external booking reference
  origin           CHAR(3)     NOT NULL,   -- IATA code
  destination      CHAR(3)     NOT NULL,   -- IATA code
  depart_time      TIMESTAMP   NOT NULL,
  return_time      TIMESTAMP,
  passengers       JSONB       NOT NULL,   -- [{ "name": "...", "age": 30, "seat": "12A" }, ...]
  price            NUMERIC(10,2) NOT NULL,
  currency         CHAR(3)     NOT NULL,
  created_at       TIMESTAMP   NOT NULL DEFAULT now()
);
```

---

### 2.2 Hotel Bookings

```sql
CREATE TABLE hotel_bookings (
  hotel_id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  provider         VARCHAR(50) NOT NULL,   -- e.g. "Booking.com"
  booking_ref      VARCHAR(100) NOT NULL,
  hotel_name       VARCHAR(255) NOT NULL,
  checkin_date     DATE        NOT NULL,
  checkout_date    DATE        NOT NULL,
  rooms            JSONB       NOT NULL,   -- [{ "type": "Double", "guests": 2 }, ...]
  price_per_night  NUMERIC(10,2) NOT NULL,
  total_nights     INT         NOT NULL,
  currency         CHAR(3)     NOT NULL,
  created_at       TIMESTAMP   NOT NULL DEFAULT now()
);
```

---

### 2.3 Car Rentals

```sql
CREATE TABLE car_rentals (
  car_id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  provider         VARCHAR(50) NOT NULL,   -- e.g. "Hertz"
  booking_ref      VARCHAR(100) NOT NULL,
  pick_up_location VARCHAR(255) NOT NULL,
  pick_up_date     TIMESTAMP   NOT NULL,
  drop_off_location VARCHAR(255) NOT NULL,
  drop_off_date    TIMESTAMP   NOT NULL,
  vehicle_details  JSONB       NOT NULL,   -- { "make": "Toyota", "model": "Camry", "category": "SUV" }
  price_per_day    NUMERIC(10,2) NOT NULL,
  total_days       INT         NOT NULL,
  currency         CHAR(3)     NOT NULL,
  created_at       TIMESTAMP   NOT NULL DEFAULT now()
);
```

---

### 2.4 Tours & Experiences

```sql
CREATE TABLE tour_bookings (
  tour_id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  provider         VARCHAR(50) NOT NULL,   -- e.g. "Viator"
  booking_ref      VARCHAR(100) NOT NULL,
  tour_name        VARCHAR(255) NOT NULL,
  scheduled_date   DATE        NOT NULL,
  participants     JSONB       NOT NULL,   -- [{ "name": "...", "age": 28 }, ...]
  price_per_person NUMERIC(10,2) NOT NULL,
  total_price      NUMERIC(12,2) NOT NULL,
  currency         CHAR(3)     NOT NULL,
  created_at       TIMESTAMP   NOT NULL DEFAULT now()
);
```

---

## 3. Payments

```sql
CREATE TABLE payments (
  payment_id     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id     UUID        NOT NULL REFERENCES bookings(booking_id),
  amount         NUMERIC(12,2) NOT NULL,
  currency       CHAR(3)     NOT NULL,
  method         VARCHAR(20) NOT NULL CHECK (method IN ('stripe','paypal')),
  provider_ref   VARCHAR(255) NOT NULL,    -- payment gateway transaction ID
  status         VARCHAR(20) NOT NULL CHECK (status IN ('initiated','succeeded','failed')),
  created_at     TIMESTAMP   NOT NULL DEFAULT now()
);
```

---

## 4. Conversation & Memory

```sql
-- Chat/voice session
CREATE TABLE conversation_sessions (
  session_id     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID        NOT NULL REFERENCES users(user_id),
  started_at     TIMESTAMP   NOT NULL DEFAULT now(),
  ended_at       TIMESTAMP
);

-- Individual messages (both user and agent)
CREATE TABLE conversation_messages (
  message_id     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id     UUID        NOT NULL REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
  sender         VARCHAR(10) NOT NULL CHECK (sender IN ('user','agent')),
  modality       VARCHAR(10) NOT NULL CHECK (modality IN ('text','voice')),
  content        TEXT        NOT NULL,
  timestamp      TIMESTAMP   NOT NULL DEFAULT now()
);

-- Long-term vector memory (for personalization, recommendations)
CREATE TABLE memory_vectors (
  vector_id      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  session_id     UUID        REFERENCES conversation_sessions(session_id),
  content_ref    UUID,                             -- optional link to message or booking
  embedding       VECTOR     NOT NULL,              -- e.g. pgvector column
  metadata       JSONB,
  created_at     TIMESTAMP   NOT NULL DEFAULT now()
);
```

---

## 5. Third-Party API Credentials

```sql
CREATE TABLE api_credentials (
  cred_id        UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID        NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  provider       VARCHAR(50) NOT NULL,               -- e.g. "Amadeus", "Booking.com"
  credentials    JSONB       NOT NULL,               -- { "api_key": "...", "secret": "..." }
  created_at     TIMESTAMP   NOT NULL DEFAULT now(),
  updated_at     TIMESTAMP   NOT NULL DEFAULT now()
);
```

---
