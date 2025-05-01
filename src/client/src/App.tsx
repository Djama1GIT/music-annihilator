import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { router } from "./routes";
import './App.css';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          {router.map((route) => (
            <Route key={route.path} path={route.path} element={route.element}/>
          ))}
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default React.memo(App);