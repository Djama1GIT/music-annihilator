import React from "react";
import { Col, Row, Typography } from "antd";
import styles from "./Title.module.scss";

const { Title, Text } = Typography;

const TitleComponent: React.FC = () => {
  return (
    <Row justify="center" className={styles.titleRow}>
      <Col xs={24} md={18} lg={16}>
        <Title level={2} className={styles.mainTitle}>
          Удалите музыку из любого аудиофайла при помощи искусственного интеллекта!
        </Title>
        <Text type="secondary" className={styles.subtitle}>
          Загрузите аудиофайл, и наш искусственный интеллект удалит из нее музыку.
          Поддерживаемые форматы: MP3, WAV, FLAC, AAC и другие.
        </Text>
      </Col>
    </Row>
  );
};

export default React.memo(TitleComponent);