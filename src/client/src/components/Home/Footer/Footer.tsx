import React from 'react';
import { Row, Col, Typography, Layout, theme } from 'antd';
import styles from './Footer.module.scss';

const { Footer: AntFooter } = Layout;
const { Title, Text } = Typography;

const FooterComponent: React.FC = () => {
  const currentYear: number = new Date().getFullYear();

  return (
    <AntFooter className={styles.footer}>
      <Row gutter={[24, 24]}>
        <Col xs={24} md={8}>
          <Title level={5} className={styles.footerTitle}>Music Annihilator</Title>
          <Text type="secondary">
            Инструмент для удаления музыки с помощью AI
          </Text>
        </Col>
        <Col xs={24} md={8}>
          <Title level={5} className={styles.footerTitle}>Контакты</Title>
          <Text type="secondary">musicannihilator@dj.ama1.ru</Text>
        </Col>
        <Col xs={24} md={8}>
          <Title level={5} className={styles.footerTitle}>Правовая информация</Title>
          <Text type="secondary">© {currentYear} Music Annihilator</Text>
          <br />
          <Text type="secondary">Все права защищены</Text>
        </Col>
      </Row>
    </AntFooter>
  );
};

export default React.memo(FooterComponent);