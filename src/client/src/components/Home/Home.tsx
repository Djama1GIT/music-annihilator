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
} from 'antd';
import {
  UploadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import type { UploadProps } from 'antd';
import styles from './Home.module.scss';

const { Header, Content, Footer } = Layout;
const { Title, Text } = Typography;

const AudioProcessingHomepage: React.FC = () => {
  const [fileList, setFileList] = useState<any[]>([]);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
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

  return (
    <Layout className={styles.layout}>
      <Header className={styles.header}>
        <div className={styles.headerContent}>
          <Title level={3} className={styles.title}>
            Music Annihilator
          </Title>
        </div>
      </Header>

      <Content className={styles.content}>
        <Row justify="center" className={styles.titleRow}>
          <Col xs={24} md={18} lg={16}>
            <Title level={2} className={styles.mainTitle}>
              Отделите вокал от музыки с помощью искусственного интеллекта
            </Title>
            <Text type="secondary" className={styles.subtitle}>
              Загрузите песню, и наш искусственный интеллект разделит вокал и инструменты на разные треки
            </Text>
          </Col>
        </Row>

        <Row justify="center">
          <Col xs={24} md={18} lg={12}>
            <Card hoverable>
              <Upload.Dragger
                name="file"
                multiple={false}
                accept="audio/*"
                fileList={fileList}
                onChange={handleUpload}
                beforeUpload={() => false} // Prevent automatic upload
                className={styles.dragger}
              >
                <UploadOutlined className={styles.uploadIcon} />
                <Title level={4} className={styles.uploadTitle}>Щелкните или перетащите аудиофайл сюда</Title>
                <Text type="secondary">Поддерживает MP3, WAV, FLAC и другие форматы</Text>
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
                >
                  {processing ? 'Обработка...' : 'Начать обработку'}
                </Button>

                {processing && (
                  <div>
                    <Text strong>Отделение вокала от музыки...</Text>
                    <Progress percent={progress} status="active" />
                  </div>
                )}

                {progress === 100 && (
                  <Alert
                    message="Обработка завершена!"
                    type="success"
                    showIcon
                    action={
                      <Space>
                        <Button
                          icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                          onClick={togglePlayback}
                        >
                          {isPlaying ? 'Пауза' : 'Играть'}
                        </Button>
                        <Button
                          type="primary"
                          icon={<DownloadOutlined />}
                          onClick={downloadResult}
                        >
                          Download
                        </Button>
                      </Space>
                    }
                  />
                )}

                <audio ref={audioRef} src={fileList[0]?.url} className={styles.hiddenAudio} />
              </Space>
            </Card>
          </Col>
        </Row>
      </Content>

      <Footer className={styles.footer}>
        <Space direction="vertical" size="middle">
          <Text type="secondary">
            © {new Date().getFullYear()} Music Annihilator. Все права защищены.
          </Text>
        </Space>
      </Footer>
    </Layout>
  );
};

export default AudioProcessingHomepage;