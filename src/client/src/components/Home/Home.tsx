import React, { useState, useEffect } from 'react';
import { ConfigProvider, Layout, theme, App, Switch } from 'antd';
import styles from './Home.module.scss';

import Header from "./Header/Header";
import Content from "./Content/Content";
import Footer from "./Footer/Footer";

const Homepage: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme ? savedTheme === 'dark' : false;
  });

  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const handleThemeChange = (checked: boolean) => {
    setIsDarkMode(checked);
  };

  return (
    <App>
      <ConfigProvider
        theme={{
          algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
          components: {
            Layout: {
              colorBgHeader: isDarkMode ? "#111" : "#fff",
              colorBgBody: isDarkMode ? "#000" : "#f7f7f7",
              colorBgLayout: isDarkMode ? "#111" : "#fff",
            },
          },
          cssVar: true,
          hashed: false,
        }}
      >
        <Layout className={styles.layout}>
          <Header isDarkMode={isDarkMode} handleThemeChange={handleThemeChange}/>
          <Content />
          <Footer />
        </Layout>
      </ConfigProvider>
    </App>
  );
};

export default React.memo(Homepage);