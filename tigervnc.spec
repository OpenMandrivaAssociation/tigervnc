%define _disable_rebuild_configure 1
%define _disable_lto 1
%define _disable_ld_no_undefined 1

# snapshotver is year-month-day-svnrevision, generated by "make dist"
%define snapshot		0
%define snapshotversion 20140212svn5159

Summary:	Viewer for the VNC remote display system
Name:		tigervnc
Version:	1.13.1
%if %{snapshot}
Release:	0.%{snapshotversion}.1
Source0:	%{name}-%{version}-%{snapshotversion}.tar.gz
%else
Release:	2
Source0:	https://github.com/TigerVNC/tigervnc/archive/v%{version}.tar.gz
%endif
License:	GPLv2+
URL:		https://www.tigervnc.com/
Group:		Networking/Remote access
Source1:	vncviewer.desktop
Source3:	vncserver.service
Source5:	10-libvnc.conf
# we put cmake build into a different dir (from us, then mga, then back here :)
Patch1:		tigervnc-1.8.90-mga-buildir.patch
Patch2:		tigervnc-1.2.80-link.patch

#(proyvind): FIXME: this one got fscked, needs to be fixed in Makefile.am, so
# that miext/sync/libsync.la gets built first...
#Patch18: tigervnc-1.0.90-link-against-forgotten-local-library.patch

BuildRequires:	x11-server-source
BuildRequires:	gettext-devel
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(dri)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(xi)
BuildRequires:	pkgconfig(xtst)
BuildRequires:	pkgconfig(libxcvt)
BuildRequires:	x11-font-util
BuildRequires:	x11-util-macros
BuildRequires:	pkgconfig(xtrans)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(xkbfile)
BuildRequires:	pkgconfig(xfont)
BuildRequires:	pkgconfig(xfont2)
BuildRequires:	pkgconfig(pixman-1)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(pciaccess)
BuildRequires:	pam-devel
BuildRequires:	pkgconfig(gnutls)
BuildRequires:	pkgconfig(xrender)
BuildRequires:	imagemagick
BuildRequires:	nasm
BuildRequires:	java-devel
BuildRequires:	autoconf
BuildRequires:	cmake
BuildRequires:	fltk-devel >= 1.3.3
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:	pkgconfig(libjpeg)
Provides:	vncviewer
Conflicts:	tightvnc

%description
Virtual Network Computing (VNC) is a remote display system which
allows you to view a computing 'desktop' environment not only on the
machine where it is running, but from anywhere on the Internet and
from a wide variety of machine architectures.  This package contains a
client which will allow you to connect to other desktops running a VNC
server.

%files -f %{name}.lang
%doc README.rst
%{_bindir}/vncviewer
%{_iconsdir}/*
%{_datadir}/applications/*
%{_mandir}/man1/vncviewer.1*
%{_datadir}/metainfo/org.tigervnc.vncviewer.metainfo.xml

#------------------------------------------------------------------------------

%package server
Summary:	Server for the VNC remote display system
Group:		Networking/Remote access

# Old RealVNC package:
Provides:	vnc-server
Conflicts:	tightvnc-server

Requires:	vnc-server-common

%description server
The VNC system allows you to access the same desktop from a wide
variety of platforms.  This package is a TigerVNC server, allowing
others to access the desktop on your machine.

%files server
%{_bindir}/vncconfig
%{_bindir}/vncpasswd
%{_bindir}/x0vncserver
%{_bindir}/Xvnc
%{_mandir}/man1/Xvnc.1*
%{_mandir}/man1/vncpasswd.1*
%{_mandir}/man1/vncconfig.1*
%{_mandir}/man1/x0vncserver.1*
%{_unitdir}/vncserver@.service
%{_sysconfdir}/pam.d/tigervnc
%dir %{_sysconfdir}/tigervnc
%{_sysconfdir}/tigervnc/vncserver-config-defaults
%{_sysconfdir}/tigervnc/vncserver-config-mandatory
%{_sysconfdir}/tigervnc/vncserver.users
%{_bindir}/vncsession
%{_libexecdir}/vncserver
%{_libexecdir}/vncsession-start
%doc %{_docdir}/tigervnc
%{_mandir}/man8/vncserver.8*
%{_mandir}/man8/vncsession.8*

#------------------------------------------------------------------------------

%package server-module
Summary:	Xorg module for the VNC remote display system
Group:		Networking/Remote access
Provides:	vnc-server-module
Requires:	x11-server-xorg

%description server-module
This package contains libvnc.so module to X server, allowing others
to access the desktop on your machine.

%files server-module
%{_libdir}/xorg/modules/extensions/libvnc.so
%config %{_sysconfdir}/X11/xorg.conf.d/10-libvnc.conf

#------------------------------------------------------------------------------

%package java

Summary:	Java viewer for the VNC remote display system
Group:		Networking/Remote access
# Old RealVNC package:
Provides:	vnc-java
Conflicts:	tightvnc-java

# "TightVNC-specific" is not a typo, see the README file located inside the
# java source tree
%description java
This distribution is based on the standard VNC source and includes new
TightVNC-specific features and fixes, such as additional low-bandwidth
optimizations, major GUI improvements, and more.

There are three basic ways to use TigerVNC Java viewer:
  1. Running applet as part of TigerVNC server installation.
  2. Running applet hosted on a standalone Web server.
  3. Running the viewer as a standalone application.

%files java
%{_datadir}/java/*.jar
%{_datadir}/%{name}

#------------------------------------------------------------------------------

%prep
%if %{snapshot}
%autosetup -p1 -n %{name}-%{version}-%{snapshotversion}
%else
%autosetup -p1
%endif
cp -r /usr/share/x11-server-source/* unix/xserver
pushd unix/xserver
for all in `find . -type f -perm -001`; do
	chmod -x "$all"
done
patch -p1 -b -z .xserver~ <../xserver21.1.1.patch
popd


%build
# Temporary build with -fno-omit-frame-pointer, it causes problems
export CFLAGS="%{optflags} -fno-omit-frame-pointer"
export CXXFLAGS="$CFLAGS"
export JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8

%cmake -G Ninja
%ninja_build
cd ..

# XXX: I'm not sure this define is actually needed
# Need this for shared objects that reference X Server, or other modules symbols
# Search for modules in extra_module_dir before the default path.
# This will allow fglrx to install its modified modules in more cleaner way.
%define extra_module_dir %{_libdir}/xorg/extra-modules

pushd unix/xserver
rm -f configure
autoreconf -fiv

# After the "--disable-config-hal", most options are just a paste from
# Mandriva's x11-server. We need to check what we can clean here (without
# reducing features)
#export CC=gcc
%configure  --disable-xorg \
		--disable-xwin \
		--disable-xvfb \
		--disable-xnest \
		--disable-dmx \
		--disable-xfbdev \
		--disable-xephyr \
		--disable-kdrive \
		--disable-xwayland \
		--disable-config-dbus \
		--enable-glx --disable-dri --enable-dri2 \
		--disable-config-hal \
		--disable-selective-werror \
		--disable-static \
		--disable-unit-tests \
		--with-log-dir=%{_logdir} \
		--without-dtrace \
		--with-os-vendor="OpenMandriva" \
		--with-os-name="`echo \`uname -s -r\` | sed -e s'/ /_/g'`" \
		--with-vendor-web="http://openmandriva.org" \
		--with-extra-module-dir=%{extra_module_dir} \
		--enable-xwrapper \
		--enable-pam \
		--with-default-font-path="catalogue:%{_sysconfdir}/X11/fontpath.d"

%make
popd

# Build icons
pushd media
%cmake -G Ninja
%ninja_build
cd ..
popd

# Build java
pushd java
%cmake -G Ninja
%ninja_build
cd ..
popd

%install
pushd build
%ninja_install
popd

pushd unix/xserver/hw/vnc
%make_install
popd

# Install systemd unit file
mkdir -p %{buildroot}%{_unitdir}
install -m644 %{SOURCE3} %{buildroot}%{_unitdir}/vncserver@.service
rm -rf %{buildroot}%{_initrddir}

# Install desktop stuff
mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/{16x16,24x24,48x48}/apps

pushd media/icons
	for s in 16 24 48; do
	install -m644 tigervnc_$s.png %{buildroot}/%{_datadir}/icons/hicolor/${s}x$s/apps/tigervnc.png
	done
popd

desktop-file-install \
	--dir %{buildroot}%{_datadir}/applications \
	%{SOURCE1}

%find_lang %{name} %{name}.lang

mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/
install -c -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/10-libvnc.conf

# remove unwanted files
rm -f  %{buildroot}/%{_libdir}/xorg/modules/extensions/libvnc.la
rm -rf  %{buildroot}/%{_datadir}/doc/%{name}-%{version}

# java
install -d -m 755 %{buildroot}%{_datadir}/java
install -d -m 755 %{buildroot}%{_datadir}/%{name}/classes
pushd java/build
	install -m 755 VncViewer.jar %{buildroot}%{_datadir}/%{name}/classes/vncviewer-%{version}.jar
popd

pushd %{buildroot}%{_datadir}/%{name}/classes
	mv vncviewer-%{version}.jar %{buildroot}%{_datadir}/java
	ln -s %{_datadir}/java/vncviewer-%{version}.jar VncViewer.jar
popd

pushd %{buildroot}%{_datadir}/java
	ln -s vncviewer-%{version}.jar vncviewer.jar
	ln -s vncviewer-%{version}.jar VncViewer.jar
popd
