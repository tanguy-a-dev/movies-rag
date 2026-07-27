import { BrowserRouter, NavLink, Route, Routes } from "react-router";
import ChatPage from "./pages/ChatPage";
import SearchPage from "./pages/SearchPage";
import "./App.css";

function navLinkClass({ isActive }: { isActive: boolean }): string {
  return isActive ? "active" : "";
}

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="app-nav">
          <span className="app-title">MoviesRAG</span>
          <div className="app-tabs">
            <NavLink to="/" end className={navLinkClass}>
              Chat
            </NavLink>
            <NavLink to="/search" className={navLinkClass}>
              Search
            </NavLink>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/search" element={<SearchPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
