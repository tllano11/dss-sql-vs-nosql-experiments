CXX=g++
RM=rm -f
CPPFLAGS+=-g
LDFLAGS+=-g

SRCS=csv.cpp crjoin.cpp
OBJS=$(subst .cpp,.o,$(SRCS))

all: crjoin

crjoin: $(OBJS)
	$(CXX) $(LDFLAGS) -o crjoin $(OBJS)

depend: .depend

.depend: $(SRCS)
	$(RM) ./.depend
	$(CXX) $(CPPFLAGS) -MM $^ >> ./.depend

clean:
	$(RM) $(OBJS)

distclean: clean
	$(RM) *~ .depend
	$(RM) crjoin

include .depend
