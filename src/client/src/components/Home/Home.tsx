import React, { useState, useRef } from 'react';
import {
  Upload,
  Button,
  Card,
  Row,
  Col,
  Typography,
  Divider,
  Space,
  Progress,
  Alert,
  Layout,
  Modal,
} from 'antd';
import {
  UploadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  DownloadOutlined,
  QuestionCircleOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import type { UploadProps } from 'antd';
import styles from './Home.module.scss';
import Paragraph from "antd/lib/typography/Paragraph";

const { Header, Content, Footer } = Layout;
const { Title, Text } = Typography;

const AudioProcessingHomepage: React.FC = () => {
  const [fileList, setFileList] = useState<any[]>([]);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const [isModalVisible, setIsModalVisible] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const handleUpload: UploadProps['onChange'] = (info) => {
    let newFileList = [...info.fileList];

    newFileList = newFileList.slice(-1);
    newFileList = newFileList.map(file => {
      if (file.response) {
        file.url = file.response.url;
      }
      return file;
    });

    setFileList(newFileList);
  };

  const startProcessing = () => {
    if (fileList.length === 0) return;

    setProcessing(true);
    setProgress(0);

    // Simulate processing progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setProcessing(false);
          return 100;
        }
        return prev + 10;
      });
    }, 500);
  };

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const downloadResult = () => {
    alert('Загрузка результата обработки...');
  };

  const showModal = () => {
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
  };

  return (
    <Layout className={styles.layout}>
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
            icon={<QuestionCircleOutlined />}
            className={styles.howItWorksButton}
            onClick={showModal}
          >
            Как это работает
          </Button>
        </div>
      </Header>

      <Modal
        title={
          <div>
            <QuestionCircleOutlined/>
            <span> Как это работает</span>
          </div>
        }
        open={isModalVisible}
        onCancel={handleCancel}
        footer={[
          <Button key="close" onClick={handleCancel}>
            Закрыть
          </Button>
        ]}
        width={800}
      >
        <Title level={4}>Технология Spleeter</Title>
        <Paragraph>
          Наш сервис использует технологию Spleeter, разработанную для разделения аудио с помощью искусственного интеллекта.
        </Paragraph>

        <Title level={5}>Основные возможности:</Title>
        <ul>
          <li>Поддержка 2, 4 и 5 стемов (отдельных дорожек)</li>
          <li>Высокое качество разделения благодаря нейросетевой модели</li>
          <li>Быстрая обработка даже длинных треков</li>
        </ul>

        <Title level={5}>Как это работает технически:</Title>
        <Paragraph>
          Spleeter использует предобученную модель U-Net, которая была обучена на большом наборе данных для распознавания и разделения различных компонентов аудио.
          Алгоритм анализирует спектрограмму аудиофайла и выделяет отдельные составляющие.
        </Paragraph>
      </Modal>

      <Content className={styles.content}>
        <Row justify="center" className={styles.titleRow}>
          <Col xs={24} md={18} lg={16}>
            <Title level={2} className={styles.mainTitle}>
              Удалите музыку из аудиофайла при помощи искусственного интеллекта!
            </Title>
            <Text type="secondary" className={styles.subtitle}>
              Загрузите аудиофайл, и наш искусственный интеллект удалит из нее музыку.
              Поддерживаемые форматы: MP3, WAV, FLAC, AAC и другие.
            </Text>
          </Col>
        </Row>

        <Row justify="center">
          <Col xs={24} md={18} lg={12}>
            <Card hoverable className={styles.uploadCard}>
              <Upload.Dragger
                name="file"
                multiple={false}
                accept="audio/*"
                fileList={fileList}
                onChange={handleUpload}
                beforeUpload={() => false}
                className={styles.dragger}
              >
                <UploadOutlined className={styles.uploadIcon} />
                <Title level={4} className={styles.uploadTitle}>Перетащите аудиофайл сюда</Title>
                <Text type="secondary">или нажмите для выбора файла</Text>
                <div className={styles.fileTypes}>
                  <Text type="secondary">MP3, WAV, FLAC, AAC, OGG</Text>
                </div>
              </Upload.Dragger>

              <Divider />

              <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                  type="primary"
                  size="large"
                  block
                  onClick={startProcessing}
                  disabled={fileList.length === 0 || processing}
                  loading={processing}
                  className={styles.processButton}
                >
                  {processing ? 'Обработка...' : 'Начать обработку'}
                </Button>

                {processing && (
                  <div className={styles.progressContainer}>
                    <Text strong>Удаление музыки из аудио...</Text>
                    <Progress
                      percent={progress}
                      status="active"
                      strokeColor={{
                        '0%': '#108ee9',
                        '100%': '#87d068',
                      }}
                    />
                    <Text type="secondary" className={styles.progressTip}>
                      Обычно обработка занимает 1-2 минуты в зависимости от длины файла
                    </Text>
                  </div>
                )}

                {progress === 100 && (
                  <Alert
                    message={
                      <Space>
                        <span>Обработка завершена!</span>
                        <Text type="success">Готово за 1 мин 23 сек</Text>
                      </Space>
                    }
                    type="success"
                    showIcon
                    action={
                      <Space>
                        <Button
                          icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                          onClick={togglePlayback}
                          className={styles.playButton}
                        >
                          {isPlaying ? 'Пауза' : 'Прослушать'}
                        </Button>
                        <Button
                          type="primary"
                          icon={<DownloadOutlined />}
                          onClick={downloadResult}
                        >
                          Скачать результат
                        </Button>
                      </Space>
                    }
                    className={styles.resultAlert}
                  />
                )}

                <audio ref={audioRef} src={fileList[0]?.url} className={styles.hiddenAudio} />
              </Space>
            </Card>
          </Col>
        </Row>

        <Row gutter={[24, 24]} className={styles.featuresRow}>
          <Col xs={24} md={12} lg={8}>
            <Card hoverable className={styles.featureCard}>
              <div className={styles.featureIcon}>
                <PlayCircleOutlined />
              </div>
              <Title level={4} className={styles.featureTitle}>Высокое качество</Title>
              <Text>
                Наш алгоритм сохраняет качество оригинальной аудиозаписи, сохраняя все важные детали звука, минимизируя артефакты и шумы
              </Text>
            </Card>
          </Col>
          <Col xs={24} md={12} lg={8}>
            <Card hoverable className={styles.featureCard}>
              <div className={styles.featureIcon}>
                <RocketOutlined />
              </div>
              <Title level={4} className={styles.featureTitle}>Быстрая обработка</Title>
              <Text>
                Высокая скорость обработки благодаря новейшим технологиям
              </Text>
            </Card>
          </Col>
          <Col xs={24} md={12} lg={8}>
            <Card hoverable className={styles.featureCard}>
              <div className={styles.featureIcon}>
                <UploadOutlined />
              </div>
              <Title level={4} className={styles.featureTitle}>Множество форматов</Title>
              <Text>
                Обрабатывайте аудиофайлы любых удобных для вас форматов: MP3, WAV, FLAC, AAC и многие другие
              </Text>
            </Card>
          </Col>
        </Row>
      </Content>

      <Footer className={styles.footer}>
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
            <Text type="secondary">© {new Date().getFullYear()} Music Annihilator</Text>
            <br />
            <Text type="secondary">Все права защищены</Text>
          </Col>
        </Row>
      </Footer>
    </Layout>
  );
};

export default AudioProcessingHomepage;