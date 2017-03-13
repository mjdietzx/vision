import torch.utils.data as data

from PIL import Image
import os
import os.path

IMG_EXTENSIONS = [
    '.jpg', '.JPG', '.jpeg', '.JPEG',
    '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]


def is_image_file(filename):
    return any(filename.endswith(extension) for extension in IMG_EXTENSIONS)


def find_classes(dir):
    classes = [d for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]
    classes.sort()
    class_to_idx = {classes[i]: i for i in range(len(classes))}
    return classes, class_to_idx


def make_dataset(dir, class_to_idx):
    images = []
    for target in class_to_idx.keys():
        d = os.path.join(dir, target)
        if not os.path.isdir(d):
            continue

        for root, _, fnames in sorted(os.walk(d)):
            for fname in fnames:
                if is_image_file(fname):
                    path = os.path.join(root, fname)
                    item = (path, class_to_idx[target])
                    images.append(item)

    return images


def default_loader(path):
    return Image.open(path).convert('RGB')


class ImageFolder(data.Dataset):
    """
    A class representing a directory of images as a `Dataset`.

    Args:
        root (String): The path to the directory.
        transform (Object): A callable object that transforms images. See: torchvision/transforms.py. By default no
                            transformations will be applied to images.
        target_transform (Object): A callable object that transforms targets (labels). By default no transformations
                                   will be applied to targets.
        loader (Function): Loads an image and returns it in a usable form. By default loads images by
                           their path and returns a `PIL.Image` instance.
        classes (List/Tuple): The sub-directories of `root` that correspond to the classes of this data set. By default
                              all sub-directories of `root` are used.

    Example:
        >>> dataset = folder.ImageFolder('./dataset', transform=transforms.Compose([
        >>>     transforms.Scale(size=224),
        >>>     transforms.RandomCrop(size=224),
        >>>     transforms.ToTensor()
        >>> ]), classes=['cat', 'dog'])
    """

    def __init__(self, root, transform=None, target_transform=None, loader=default_loader, classes=None):
        if not classes:
            classes, class_to_idx = find_classes(root)
        else:
            class_to_idx = {classes[i]: i for i in range(len(classes))}

        imgs = make_dataset(root, class_to_idx)

        if len(imgs) == 0:
            print('Didn\'t find any class dirs in `root`. Trying to find class dirs in all sub dirs of root...')
            imgs = []
            for dir in os.listdir(root):
                dir_path = os.path.join(root, dir)
                if os.path.isdir(dir_path):
                    imgs.extend(make_dataset(dir_path, class_to_idx))

            if len(imgs) == 0:
                raise(RuntimeError("Found 0 images in subfolders of: " + root + "\n"
                                   "Supported image extensions are: " + ",".join(IMG_EXTENSIONS)))

        self.root = root
        self.imgs = imgs
        self.classes = classes
        self.class_to_idx = class_to_idx
        self.transform = transform
        self.target_transform = target_transform
        self.loader = loader

    def __getitem__(self, index):
        path, target = self.imgs[index]
        img = self.loader(path)
        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        return len(self.imgs)
