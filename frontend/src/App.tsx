import './App.css';
import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">TravelPal</h1>
          <p className="text-lg text-gray-600">Your AI-powered travel assistant</p>
        </div>
        
        <div className="flex justify-center">
          <div className="w-full max-w-2xl">
            <ChatWidget />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
