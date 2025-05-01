import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { router } from "./routes";
import './App.css';
import { ConfigProvider, theme } from "antd";

const App: React.FC = () => {
  const savedTheme = localStorage.getItem('theme');
  const isDarkMode = savedTheme === 'dark';
  document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');

  return (
    <BrowserRouter>
      <ConfigProvider
        theme={{
          algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
        }}
      >
        <div className="App">
          <Routes>
            {router.map((route) => (
              <Route key={route.path} path={route.path} element={route.element}/>
            ))}
          </Routes>
        </div>
      </ConfigProvider>
    </BrowserRouter>
  );
}

export default React.memo(App);