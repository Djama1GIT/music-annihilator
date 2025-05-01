import { create } from 'zustand';
import { UploadFile } from "antd";

type Theme = 'dark' | 'light';

interface AnnihilatorStoreState {
  theme: Theme;
  aboutModalVisible: boolean;

  fileList: UploadFile[];
  isUploading: boolean;
  isProcessing: boolean;
  progress: number;
  isPlaying: boolean;

  setTheme: (theme: Theme) => void;
  setAboutModalVisible: (visible: boolean) => void;

  setFileList: (fileList: UploadFile[]) => void;
  setIsUploading: (uploading: boolean) => void;
  setIsProcessing: (isProcessing: boolean) => void;
  setProgress: (progress: number | ((prev: number) => number)) => void;
  setIsPlaying: (isPlaying: boolean) => void;
}

export const useAnnihilatorStore = create<AnnihilatorStoreState>((set) => ({
  theme: (window.localStorage.getItem('theme') as Theme) || 'dark',
  aboutModalVisible: false,

  fileList: [],
  isUploading: false,
  isProcessing: false,
  progress: 0,
  isPlaying: false,

  setTheme: (theme: Theme) => {
    set({ theme });
    window.localStorage.setItem('theme', theme);
  },
  setAboutModalVisible: (visible: boolean) => set({ aboutModalVisible: visible }),

  setFileList: (fileList: UploadFile[]) => set({ fileList }),
  setIsUploading: (isUploading: boolean) => set({ isUploading }),
  setIsProcessing: (isProcessing: boolean) => set({ isProcessing }),
  setProgress: (progress: number | ((prev: number) => number)) =>
    set(state => ({
      progress: typeof progress === 'function' ? progress(state.progress) : progress,
    })),
  setIsPlaying: (isPlaying: boolean) => set({ isPlaying }),
}));