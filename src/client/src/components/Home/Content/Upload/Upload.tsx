import React, { useRef, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  Divider,
  Progress,
  Row,
  Space,
  Typography,
  Upload,
  UploadFile,
  UploadProps
} from "antd";
import { DownloadOutlined, PauseCircleOutlined, PlayCircleOutlined, UploadOutlined } from "@ant-design/icons";
import styles from "./Upload.module.scss";

const { Text, Title } = Typography;

const UploadComponent: React.FC = () => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const [processing, setProcessing] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

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

  const startProcessing = (): void => {
    if (fileList.length === 0) return;

    setUploading(true);
    setProgress(0);

    const uploadInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 50) {
          clearInterval(uploadInterval);
          setUploading(false);
          startActualProcessing();
          return 50;
        }
        return prev + 5;
      });
    }, 300);
  };

  const startActualProcessing = (): void => {
    setProcessing(true);

    const processingInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(processingInterval);
          setProcessing(false);
          return 100;
        }
        return prev + 1;
      });
    }, 200);
  };

  const togglePlayback = (): void => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const downloadResult = (): void => {
    alert('Загрузка результата обработки...');
  };

  const uploadProps: UploadProps = {
    name: "file",
    multiple: false,
    accept: "audio/*",
    fileList,
    onChange: handleUpload,
    beforeUpload: () => false,
    className: styles.dragger,
    disabled: uploading || processing
  };

  const progressStrokeColor = {
    '0%': '#108ee9',
    '100%': '#87d068',
  };

  return (
    <Row justify="center" className={styles.rowContainer}>
      <Col xs={24} md={18} lg={12}>
        <Card hoverable className={styles.uploadCard}>
          <Upload.Dragger {...uploadProps}>
            <UploadOutlined className={styles.uploadIcon}/>
            <Title level={4} className={styles.uploadTitle}>Перетащите аудиофайл сюда</Title>
            <Text type="secondary">или нажмите для выбора файла</Text>
            <div className={styles.fileTypes}>
              <Text type="secondary">MP3, WAV, FLAC, AAC, OGG</Text>
            </div>
          </Upload.Dragger>

          <Divider/>

          <Space direction="vertical" className={styles.bottomSpace}>
            <Button
              type="primary"
              size="large"
              block
              onClick={startProcessing}
              disabled={fileList.length === 0 || uploading || processing}
              loading={uploading || processing}
              className={styles.processButton}
            >
              {uploading ? 'Загрузка файла...' :
                processing ? 'Обработка...' : 'Начать обработку'}
            </Button>

            {(uploading || processing) && (
              <div className={styles.progressContainer}>
                <Text strong>
                  {uploading ? 'Загрузка файла на сервер...' : 'Удаление музыки из аудио...'}
                </Text>
                <Progress
                  percent={progress}
                  status="active"
                  strokeColor={progressStrokeColor}
                />
                <Text type="secondary" className={styles.progressTip}>
                  {uploading ? 'Пожалуйста, подождите...' :
                    'Обычно обработка занимает 1-2 минуты в зависимости от длины файла'}
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
                      icon={isPlaying ? <PauseCircleOutlined/> : <PlayCircleOutlined/>}
                      onClick={togglePlayback}
                      className={styles.playButton}
                    >
                      {isPlaying ? 'Пауза' : 'Прослушать'}
                    </Button>
                    <Button
                      type="primary"
                      icon={<DownloadOutlined/>}
                      onClick={downloadResult}
                    >
                      Скачать результат
                    </Button>
                  </Space>
                }
                className={styles.resultAlert}
              />
            )}

            <audio ref={audioRef} src={fileList[0]?.url} className={styles.hiddenAudio}/>
          </Space>
        </Card>
      </Col>
    </Row>
  );
};

export default React.memo(UploadComponent);