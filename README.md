## Boogie's AGR Repository

The [agr](https://github.com/hbiyik/agr) tool is necessary to make use of this repository.

# Precautions:

- The packages in this repository use a lot of disk space. Kodi itself only requires ~15GB to build while kernels need ~5GB. Make sure you have sufficient storage space.
- When building packages you might need extra memory during the linking process. Make sure you use big enough swap to prevent OOM kills.

# Tips:

- Compiling on low-power devices can take a lot longer. You can shorten it by running agr in arm containers https://github.com/hbiyik/agr?tab=readme-ov-file#advanced-usage-and-containers
