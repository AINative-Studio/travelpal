### Epic 1.1: Repo & Infra Setup

* **Story 1.1.1**: As a developer, I want separate Git repositories for frontend, backend, and infrastructure code so that changes remain isolated.
* **Story 1.1.2**: As a CI engineer, I want GitHub Actions workflows for linting, testing, and container builds so that PRs are validated automatically.
* **Story 1.1.3**: As a DevOps engineer, I want Terraform modules defined for Kubernetes, database, and storage so that infra is versioned and reproducible.

### Epic 1.2: LangChain Agent Bootstrapping

* **Story 1.2.1**: As an engineer, I want LangChain installed and configured so I can start building agent chains.
* **Story 1.2.2**: As a developer, I want a ConversationBufferMemory stub in place so the agent can track the current session.
* **Story 1.2.3**: As a QA engineer, I want an “echo” agent chain that returns user input so I can validate end-to-end connectivity.

### Epic 1.3: Chat UI Prototype

* **Story 1.3.1**: As a frontend dev, I want a React app scaffolded with Tailwind so I have a starting point for UI.
* **Story 1.3.2**: As a user, I want a chat widget component to send and receive messages so I can interact with the agent.
* **Story 1.3.3**: As a developer, I want the chat widget wired to the echo agent endpoint so I can verify backend integration.

---

### Epic 2.1: Voice Interface Integration

* **Story 2.1.1**: As a user, I want to record my voice in the chat widget so I can speak my requests.
* **Story 2.1.2**: As a backend dev, I want to transcribe audio to text via Whisper/Deepgram so the agent can process voice input.
* **Story 2.1.3**: As a user, I want the agent’s text responses converted to speech via Amazon Polly/openTTS so I can hear replies.

### Epic 2.2: Session & Long-Term Memory

* **Story 2.2.1**: As a backend dev, I want to persist `conversation_sessions` & `conversation_messages` so sessions can be replayed.
* **Story 2.2.2**: As an agent designer, I want ConversationBufferMemory backed by the DB so the agent retains context within a session.
* **Story 2.2.3**: As a personalization engineer, I want VectorStoreMemory (pgvector/Pinecone) so the agent can recall past preferences.

---

### Epic 3.1: Flight Search Integration

* **Story 3.1.1**: As a backend dev, I want an Amadeus/Skyscanner client module so I can call flight-search APIs.
* **Story 3.1.2**: As an agent developer, I want a `flight_search` tool chain so the agent can interpret “find flights” intents.
* **Story 3.1.3**: As a prompt engineer, I want prompt templates for flight queries so results match user parameters.

### Epic 3.2: Flight Results Presentation

* **Story 3.2.1**: As a user, I want flight result cards showing airline, price, times so I can compare options.
* **Story 3.2.2**: As a user, I want filters for price, duration, and stops so I can narrow results.
* **Story 3.2.3**: As a frontend dev, I want filter controls wired back to the agent so filtering happens server-side.

### Epic 3.3: Flight Booking

* **Story 3.3.1**: As a backend dev, I want to call the booking endpoint of the flight API so I can reserve tickets.
* **Story 3.3.2**: As a database engineer, I want to persist `flight_bookings` records so bookings are tracked.
* **Story 3.3.3**: As a user, I want email/SMS confirmations sent after booking so I have proof of purchase.

---

### Epic 4.1: Hotel Search & Booking

* **Story 4.1.1**: As a backend dev, I want a Booking.com/Expedia client so I can search hotels.
* **Story 4.1.2**: As an agent developer, I want `hotel_search` and `hotel_book` tools so the agent handles hotel workflows.
* **Story 4.1.3**: As a user, I want hotel cards with name, dates, price/night so I can choose accommodations.
* **Story 4.1.4**: As a database engineer, I want to persist `hotel_bookings` so reservations are stored.

### Epic 4.2: Car Rental Flow

* **Story 4.2.1**: As a backend dev, I want a Rentalcars.com/Hertz client for searching rentals.
* **Story 4.2.2**: As an agent designer, I want `car_search` and `car_book` chains so renting cars is seamless.
* **Story 4.2.3**: As a user, I want a car-rental UI with pick-up/drop-off controls so I can specify dates and locations.
* **Story 4.2.4**: As a database engineer, I want to persist `car_rentals` so rental details are saved.

---

### Epic 5.1: Tours & Experiences Integration

* **Story 5.1.1**: As a backend dev, I want a Viator/GetYourGuide client to fetch tour options.
* **Story 5.1.2**: As an agent developer, I want `tour_search` and `tour_book` tools so the agent offers experiences.
* **Story 5.1.3**: As a user, I want tour cards with name, date, price/person so I can book activities.
* **Story 5.1.4**: As a database engineer, I want to persist `tour_bookings` so experience reservations are tracked.

### Epic 5.2: Payment Processing

* **Story 5.2.1**: As a backend dev, I want Stripe/PayPal SDK integrated so payments can be collected.
* **Story 5.2.2**: As a user, I want a checkout UI to enter payment details so I can complete bookings.
* **Story 5.2.3**: As a database engineer, I want to persist `payments` with statuses so I can reconcile transactions.
* **Story 5.2.4**: As a user, I want clear error messages on payment failure so I know how to proceed.

---

### Epic 6.1: Personalization Engine

* **Story 6.1.1**: As a user, I want my saved preferences (seat class, budget) loaded automatically so I don’t re-enter them.
* **Story 6.1.2**: As a prompt engineer, I want agent templates that reference preferences so recommendations match my profile.
* **Story 6.1.3**: As a user, I want proactive reminders (e.g., passport expiry) so I stay ahead of trip prep.

### Epic 6.2: UX Enhancements

* **Story 6.2.1**: As a user, I want loading spinners and skeletons so I know when data is fetching.
* **Story 6.2.2**: As a frontend dev, I want responsive layout and accessibility best practices so the UI works on all devices.
* **Story 6.2.3**: As a localization engineer, I want i18n support stubbed so we can easily add languages.

### Epic 6.3: Human Support Handoff

* **Story 6.3.1**: As a user, I want to type “help” and connect to a live agent so I can resolve complex issues.
* **Story 6.3.2**: As a support agent, I want a dashboard showing session transcripts so I can pick up where the AI left off.
* **Story 6.3.3**: As a system admin, I want sessions flagged for handoff logged so I can monitor handoff volume.

---
