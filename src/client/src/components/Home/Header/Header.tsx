import React from 'react';
import { Button, Typography, Layout, Switch } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';
import styles from './Header.module.scss';
import HowItWorksModal from "./HowItWorksModal/HowItWorksModal";
import { useAnnihilatorStore } from "../../../store";

const { Header } = Layout;
const { Title, Text } = Typography;

const HeaderComponent: React.FC = () => {
  const theme = useAnnihilatorStore(state => state.theme);
  const setTheme = useAnnihilatorStore(state => state.setTheme);
  const isDarkMode = theme === 'dark';

  const setAboutModalVisible = useAnnihilatorStore(state => state.setAboutModalVisible);

  const handleThemeChange = (checked: boolean): void => {
    setTheme(checked ? 'dark' : 'light');
  };

  const showModal = (): void => {
    setAboutModalVisible(true);
  };

  return (
    <div>
      <Header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logoContainer}>
            <Title level={3} className={styles.title}>
              <span className={styles.logoText}>Music</span>
              <span className={styles.logoHighlight}>Annihilator</span>
            </Title>
            <Text type="secondary" className={styles.tagline}>
              AI-powered vocal isolation
            </Text>
          </div>

          <Button
            type="text"
            icon={<QuestionCircleOutlined/>}
            className={styles.howItWorksButton}
            onClick={showModal}
          >
            Как это работает
          </Button>
          <Switch
            checkedChildren="Темная"
            unCheckedChildren="Светлая"
            checked={isDarkMode}
            className={styles.themeToggle}
            onChange={handleThemeChange}
            title="Сменить цветовую схему"
          />
        </div>
      </Header>

      <HowItWorksModal />
    </div>
  );
};

export default React.memo(HeaderComponent);