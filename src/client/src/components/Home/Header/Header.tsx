import React, { useState } from 'react';
import { Button, Typography, Layout, Switch } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';
import styles from './Header.module.scss';
import HowItWorksModal from "./HowItWorksModal/HowItWorksModal";

const { Header } = Layout;
const { Title, Text } = Typography;

interface HeaderComponentInterface {
  isDarkMode: boolean;
  handleThemeChange: (checked: boolean) => void;
}

const HeaderComponent: React.FC<HeaderComponentInterface> = ({ isDarkMode, handleThemeChange }) => {
  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);

  const showModal = (): void => {
    setIsModalVisible(true);
  };

  const handleCancel = (): void => {
    setIsModalVisible(false);
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
          <div className={styles.themeToggle} title="Сменить цветовую схему">
            <Switch
              checkedChildren="Темная"
              unCheckedChildren="Светлая"
              checked={isDarkMode}
              onChange={handleThemeChange}
            />
          </div>
        </div>
      </Header>


      <HowItWorksModal
        isModalVisible={isModalVisible}
        handleCancel={handleCancel}
      />
    </div>
  );
};

export default React.memo(HeaderComponent);